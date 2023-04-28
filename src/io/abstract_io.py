from typing import Any, Dict, Callable
import pandas as pd
import datetime as dt
import os
from src.helpers.util import check_df_has_datetime_index, coerce_numeric
from src.util import get_file_path, get_logger, get_settings
from rx.subject import Subject  # type: ignore
from abc import ABC, abstractmethod  # , abstractmethod
from src.io.enum_io import RigDataFrame

class AbstractIO(ABC):

    def __init__(self, rig_data_frame: RigDataFrame, primary: Subject) -> None:
        super().__init__()
        self.logger = get_logger(self)
        self.df_name = rig_data_frame.value
        self.primary = primary
        self.symbol_df_dict: Dict[str, pd.DataFrame] = {}

        self.settings = get_settings('app')
        for symbols_config in self.settings['symbols_config']:
            df = self.restore_symbol_df_data(symbols_config['symbol'])
            if df is not None:
                self.symbol_df_dict[symbols_config['symbol']] = df
            else:
                self.symbol_df_dict[symbols_config['symbol']] = pd.DataFrame()
        self.init_subscriptions()

    def get_period_duration(self) -> str:
        return f"{self.settings['window']['value']}{self.settings['window']['period_type']}"

    def generic_publish_df_window(self, symbol: str, event_object: object, period_duration: pd.Timedelta | None = None) -> None:
        if period_duration is None:
            period_duration = pd.Timedelta(self.get_period_duration())
        df = self.symbol_df_dict[symbol]
        check_df_has_datetime_index(df)
        has_enough_data = self.check_df_contains_window_period(df, period_duration)
        if has_enough_data:
            pp_processors = self.get_pre_publish_processors()
            if len(pp_processors) > 0:
                self.logger.info(f"applying pre-publish processors: len: {len(pp_processors)}")
                for pp_processor in pp_processors:
                    df = pp_processor(df)
            self.symbol_df_dict[symbol] = df
            try:
                self.save_symbol_df_data(symbol)
            except Exception as e:
                self.logger.error(
                    f'append_post_processing: save_symbol_df_data: {str(e)}')        
            self.logger.debug(
                f"symbol df len: {len(df)}, period_duration: {period_duration}, start: {str(df.index.min())}, end: {str(df.index.max())}")
            window_df: pd.DataFrame = df.loc[df.index >=
                                             df.index.max() - period_duration]
            self.logger.debug(
                f"window df len: {len(window_df)}, start: {str(window_df.index.min())}, end: {str(window_df.index.max())}")
            self.primary.on_next(event_object(
                window_df, symbol))  # type: ignore
        else:
            self.logger.warning(
                f"Window Dataframe for {symbol}, with period required {str(period_duration)}, does not contain enough data")

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

    def save_symbol_df_data(self, symbol: str, name: str | None = None, df: pd.DataFrame | None = None) -> None:
        if name is None:
            name = self.df_name
        path = self.get_symbol_window_store_path(symbol, name)  # type: ignore
        if df is None:
            df = self.symbol_df_dict[symbol]
        if not df.empty:
            df_cp = df.copy()
            df_cp.reset_index(inplace=True)
            df_cp.to_feather(path, compression='lz4')

    def restore_symbol_df_data(self, symbol: str) -> pd.DataFrame | None:
        path = self.get_symbol_window_store_path(symbol, self.df_name)
        if os.path.exists(path):
            try:
                restored_df = pd.read_feather(path)
                restored_df['timestamp'] = pd.to_datetime(
                    restored_df['timestamp'])
                restored_df.set_index('timestamp', inplace=True)
                return restored_df
            except Exception as e:
                self.logger.error(f"Error restoring df: {e}")
                return None

    def get_symbol_window_store_path(self, symbol: str, df_name: str) -> str:
        return str(get_file_path(f'symbol_windows/{symbol}-{df_name}.{self.settings["storage_ext"]}'))

    def append_row(self, symbol: str, row: Any) -> None:
        self.symbol_df_dict.setdefault(symbol, pd.DataFrame())
        row['timestamp'] = pd.to_datetime(
            row['timestamp'], unit='ms')  # type: ignore
        row_as_frame = row.to_frame().T
        row_as_frame.set_index('timestamp', inplace=True)  # type: ignore
        row_as_frame = coerce_numeric(row_as_frame)
        self.symbol_df_dict[symbol] = pd.concat(  # type: ignore
            [self.symbol_df_dict[symbol], row_as_frame])
        self.append_post_processing(symbol)

    def append_rows(self, symbol: str, df_section: pd.DataFrame) -> None:
        df_section = coerce_numeric(df_section)
        self.symbol_df_dict.setdefault(symbol, pd.DataFrame())
        self.symbol_df_dict[symbol] = pd.concat(  # type: ignore
            [self.symbol_df_dict[symbol], df_section])
        self.symbol_df_dict[symbol].sort_values(
            'timestamp', inplace=True)  # type: ignore
        self.append_post_processing(symbol)

    def get_symbol_config(self, symbol: str) -> list[Any]:
        symbols_config = self.settings['symbols_config']
        return [d for d in symbols_config if d['symbol'] == symbol]

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

    def append_post_processing(self, symbol: str) -> None:
        """
        Optional override method to be implemented by child classes
        """
        pass

    @abstractmethod
    def check_df_contains_window_period(self, df: pd.DataFrame, window_period: pd.Timedelta) -> bool:
        """
        Check if a DataFrame with datetime index contains at least window_period of data.

        :window_period: pd.Timedelta (eg: kline 7 days, range_bars 27 minutes)
        :param df: Pandas DataFrame to check.
        :return: True if DataFrame contains at least 7 days of data, False otherwise.
        """
        pass

    @abstractmethod
    def init_subscriptions(self) -> None:
        pass
