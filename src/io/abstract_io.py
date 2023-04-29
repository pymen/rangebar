from typing import Any, Dict, Callable
import pandas as pd
import datetime as dt
import os
from src.helpers.util import check_df_has_datetime_index, coerce_numeric
from src.io.storage import Storage
from src.util import get_file_path, get_logger, get_settings
from rx.subject import Subject  # type: ignore
from abc import ABC, abstractmethod  # , abstractmethod
from src.io.enum_io import RigDataFrame
from functools import reduce


class AbstractIO(ABC):

    def __init__(self, rig_data_frame: RigDataFrame, primary: Subject) -> None:
        super().__init__()
        self.logger = get_logger(self)
        self.df_name = rig_data_frame.value
        self.primary = primary
        self.symbol_df_dict: Dict[str, pd.DataFrame] = {}
        self.storage = Storage(rig_data_frame, self.symbol_df_dict)

        self.settings = get_settings('app')
        for symbols_config in self.settings['symbols_config']:
            df = self.storage.restore_symbol_df_data(symbols_config['symbol'])
            if df is not None:
                self.symbol_df_dict[symbols_config['symbol']] = df
            else:
                self.symbol_df_dict[symbols_config['symbol']] = pd.DataFrame()
        self.init_subscriptions()

    def publish(self, symbol: str, event_type: object, processors_window: pd.Timedelta | int, emit_window: pd.Timedelta, batch: bool = False) -> None:
        if batch:
            self.publish_batch_df_window(symbol, event_type, processors_window)
        else:
            self.publish_df_window(
                symbol, event_type, processors_window, emit_window)

    def check_df_has_datetime_index(self, df):
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError(
                "DataFrame index must be a DatetimeIndex")

    def apply_pre_publish_processors(self, df):
        pp_processors = self.get_pre_publish_processors()
        if len(pp_processors) > 0:
            self.logger.info(
                f"applying pre-publish processors: len: {len(pp_processors)}")
            pp_result = reduce(
                lambda df, processor: processor(df), pp_processors, df)
            return pp_result
        else:
            return df

    def get_window_df(self, symbol: str, processors_window: pd.Timedelta | int, emit_window: pd.Timedelta | int) -> pd.DataFrame:
        df = self.symbol_df_dict[symbol]
        shortest_window = min(processors_window, emit_window)
        if isinstance(shortest_window, pd.Timedelta):
            window_start = max(
                df.index.min(), pd.Timestamp.now() - shortest_window)
            window_df = df.loc[df.index >= window_start]
        else:
            window_df = df.iloc[-shortest_window:]
         # Set the 'mark' column to 1 where the window_df ends.
        if not window_df.empty:
            df['mark'].iloc[-1] = 1
            self.symbol_df_dict[symbol] = df
        return window_df.copy()

    def publish_windowed_data(self, symbol: str, event_object, processors_window: pd.Timedelta | int, emit_window: pd.Timedelta | int):
        df = self.symbol_df_dict[symbol]
        self.check_df_has_datetime_index(df)
        if not self.check_df_contains_processors_window(df, processors_window):
            self.logger.warning(
                f"Window Dataframe for {symbol}, with period required {str(processors_window)}, does not contain enough data")
            return
        pp_result = self.apply_pre_publish_processors(df)
        self.symbol_df_dict[symbol] = pp_result
        try:
            self.storage.save_symbol_df_data(symbol)
        except Exception as e:
            self.logger.error(
                f'append_post_processing: save_symbol_df_data: {str(e)}')
        self.logger.debug(
            f"symbol df len: {len(pp_result)}, period_duration: {processors_window}, start: {str(pp_result.index.min())}, end: {str(pp_result.index.max())}")
        window_df = self.get_window_df(symbol, processors_window, emit_window)
        if len(window_df) > 0:
            self.logger.debug(
                f"window df len: {len(window_df)}, start: {str(window_df.index.min())}, end: {str(window_df.index.max())}")
            self.primary.on_next(event_object(window_df, symbol))

    def publish_batch_df_window(self, symbol: str, event_object: object, processors_window: pd.Timedelta | int) -> None:
        self.publish_windowed_data(
            symbol, event_object, processors_window, processors_window)

    def publish_df_window(self, symbol: str, event_object: object, processors_window: pd.Timedelta | int, emit_window: pd.Timedelta | int) -> None:
        self.publish_windowed_data(
            symbol, event_object, processors_window, emit_window)

    def get_period_duration(self) -> str:
        return f"{self.settings['window']['value']}{self.settings['window']['period_type']}"

    def prune_symbol_df_window(self, symbol: str, df: pd.DataFrame) -> None:  # type: ignore
        """
        Reduce size of in memory df, since we are only interested in 7 days
        """
        period_duration = self.get_period_duration()
        self.logger.debug(f"period_duration: {period_duration}")
        rolling_window = df.rolling(window=period_duration)  # type: ignore
        if rolling_window.has_valid_values():  # type: ignore
            # type: ignore
            window_start: dt.datetime = rolling_window.start_time[0]
            df = df[window_start:]  # type: ignore
            self.symbol_df_dict[symbol] = pd.DataFrame(rolling_window)

    def append_row(self, symbol: str, row: Any) -> None:
        self.symbol_df_dict.setdefault(symbol, pd.DataFrame())
        row['timestamp'] = pd.to_datetime(
            row['timestamp'], unit='ms')  # type: ignore
        row_as_frame = row.to_frame().T
        row_as_frame.set_index('timestamp', inplace=True)  # type: ignore
        row_as_frame = coerce_numeric(row_as_frame)
        self.symbol_df_dict[symbol] = pd.concat(  # type: ignore
            [self.symbol_df_dict[symbol], row_as_frame])
        self.post_append_trigger(symbol)

    def append_rows(self, symbol: str, df_section: pd.DataFrame) -> None:
        df_section = coerce_numeric(df_section)
        self.symbol_df_dict.setdefault(symbol, pd.DataFrame())
        self.symbol_df_dict[symbol] = pd.concat(  # type: ignore
            [self.symbol_df_dict[symbol], df_section])
        self.symbol_df_dict[symbol].sort_values(
            'timestamp', inplace=True)  # type: ignore
        self.post_append_trigger(symbol, True)

    def get_symbol_config(self, symbol: str) -> list[Any]:
        symbols_config = self.settings['symbols_config']
        return [d for d in symbols_config if d['symbol'] == symbol]

    def find_delta_for_last_mark(self, symbol: str) -> pd.Timedelta:
        df = self.symbol_df_dict[symbol]
        last_index = (df['mark'] == 1).idxmax()
        self.logger.debug(
            f"find_delta_for_last_mark: last_index: {last_index}")
        delta = pd.Timestamp.now() - last_index  # type: ignore
        return delta

    def get_pre_publish_processors(self) -> list[Callable[[pd.DataFrame], pd.DataFrame]]:
        """
        Optional override method to be implemented by child classes
        """
        return []

    def fill_historical(self, symbol: str) -> bool | None:
        """
        Optional override method to be implemented by child classes
        """
        pass

    def post_append_trigger(self, symbol: str, batch: bool = False) -> None:
        """
        Optional override method to be implemented by child classes
        """
        pass

    @abstractmethod
    def check_df_contains_processors_window(self, df: pd.DataFrame, processors_window: pd.Timedelta | int) -> bool:
        """
        Check if a DataFrame with datetime index contains at least window_period of data.

        :window_period: pd.Timedelta (eg: kline 7 days, range_bars 27 rows)
        :param df: Pandas DataFrame to check.
        :return: True if DataFrame contains at least 7 days of data, False otherwise.
        """
        pass

    @abstractmethod
    def init_subscriptions(self) -> None:
        pass
