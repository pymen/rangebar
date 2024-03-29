from typing import Any, Callable
from datetime import datetime as dt, timedelta as td
import numpy as np
import pandas as pd
from src.io.abstract_io import AbstractIO
from src.helpers.util import check_df_has_datetime_index
from src.rx import sanitize_numeric_columns_df
from src.rx.scheduler import observe_on_scheduler
from src.util import get_logger
from rx.subject import Subject  # type: ignore
from src.helpers.dataclasses import HistoricalKlineEvent, KlineWindowDataEvent, StrategyNextDataEvent
from src.helpers.dataclasses import KlineIOCmdEvent
import rx.operators as op
from src.io.enum_io import RigDataFrame


class KlineIO(AbstractIO):

    def __init__(self, primary: Subject, direct: Subject) -> None:
        super().__init__(RigDataFrame.KLINE, primary, direct)
        self.logger = get_logger(self)

    def init_subscriptions(self) -> None:
        self.primary.pipe(  # type: ignore
            op.filter(lambda o: isinstance(
                o, KlineIOCmdEvent)),  # type: ignore
            # sanitize_numeric_columns_df(),  # type: ignore
            op.map(lambda e: getattr(self, e.method)
                   (**e.kwargs)),  # type: ignore
            observe_on_scheduler()
        ).subscribe()

    def get_symbol_config(self, symbol: str) -> list[Any]:
        symbols_config = self.settings['symbols_config']
        return [d for d in symbols_config if d['symbol'] == symbol]

    def fill_historical(self, symbol: str) -> HistoricalKlineEvent | None:
        kline_df = self.symbol_df_dict[symbol]
        check_df_has_datetime_index(kline_df)
        kline_last_index: pd.Timestamp = kline_df.index[-1]  # type: ignore
        kline_first_index: pd.Timestamp = kline_df.index[0]  # type: ignore
        num_days = (kline_last_index - kline_first_index).days + 1
        self.logger.info(
            f"fill_historical: kline_last_index: {kline_last_index}, kline_first_index: {kline_first_index}, num_days: {num_days}")
        if num_days < self.settings['window']['value']:
            # Set last_timestamp to one month ago
            last_timestamp = pd.Timestamp.now(
            ) - pd.DateOffset(days=self.settings['window']['value'] + 1)
            event = HistoricalKlineEvent(
                symbol=symbol, source='kline', last_timestamp=last_timestamp)
            self.logger.info(f"fill_historical: event: {str(event)}")
            return event
        else:
            return None

    def get_pre_publish_processors(self) -> list[Callable[[pd.DataFrame], pd.DataFrame]]:
        return [self.relative_adr_range_size, self.apv]
    
    def adr(self, df: pd.DataFrame) -> float | None:
        df['date'] = df.copy().index.date  # type: ignore
        df[['high', 'low']] = df[['high', 'low']].fillna(0)   # type: ignore
        try:
            daily_high_low = df.groupby(  # type: ignore
                'date')[['high', 'low']].agg(['max', 'min'])  # type: ignore
            self.logger.debug(
                f"adr: daily_high_low: {str(daily_high_low)}")  # type: ignore
            high_max: pd.Series = daily_high_low[('high', 'max')]
            low_min: pd.Series = daily_high_low[('low', 'min')]
            # convert the Series to numeric values
            high_max = pd.to_numeric(high_max, errors='coerce')
            low_min = pd.to_numeric(low_min, errors='coerce')
            self.logger.debug(
                f"adr: high_max: {high_max.to_list()} ({type(high_max)}),  low_min: {low_min.to_list()} ({type(low_min)})")  # type: ignore
            adr = high_max - low_min  # type: ignore
            self.logger.debug(f"adr: vector subtraction: adr: {adr}")
            daily_high_low['adr'] = adr
            average_adr = np.mean(daily_high_low['adr']).item()  # type: ignore
            # type: ignore
            self.logger.info(f"result: adr: average_adr: {str(average_adr)}")
            return average_adr
        except Exception as e:
            self.logger.error(f"adr: {str(e)}")
            return None

    def relative_adr_range_size(self, df_in: pd.DataFrame, resample_arg: str = 'W') -> pd.DataFrame:
        groups = df_in.resample(resample_arg)  # type: ignore
        df_out = pd.DataFrame()
        for _, group in groups:
            week_day_seg = group.copy()
            average_adr = self.adr(week_day_seg)
            if average_adr is not None:
                week_day_seg['average_adr'] = average_adr
                df_out = pd.concat([df_out, week_day_seg])  # type: ignore
        return df_out

    def apv(self, df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
        result = df['volume'].rolling(window=window).mean()  # type: ignore
        result.fillna(0, inplace=True)   # type: ignore
        df['apv'] = result
        return df

    def check_df_contains_processors_window(self, df: pd.DataFrame, window: pd.Timedelta | int) -> bool:
        missing_date_range_limit = pd.Timedelta(minutes=1)
        debug = self.settings['debug']
        if debug:
            # FIXME there is something wrong with the debug mode - looks like it was because the time code wasn't using UTC
            missing_date_range_limit = pd.Timedelta(minutes=5) 
        missing_date_range = dt.utcnow() - df.index.max()
        date_range = df.index.max() - df.index.min()
        self.logger.debug(
            f"check_df_contains_processors_window: missing_date_range: {str(missing_date_range)}, date_range_days: {str(date_range)}, window: {str(window)}")
        if missing_date_range <= missing_date_range_limit and date_range >= window:
            return True
        else:
            self.logger.info(
                f"check_df_contains_window_period: DataFrame does not contain window period of data, yet. diff: {str(window - date_range)}")
            return False

    def publish_std_data(self, symbol: str) -> None:
            if self.direct is None:
                raise ValueError("self.direct is None")
            min_5 = pd.Timedelta(minutes=5)
            now = dt.utcnow()
            from_time = now - min_5
            df_segment = self.symbol_df_dict[symbol].copy()[from_time:]
            self.direct.on_next(StrategyNextDataEvent(symbol=symbol, df=df_segment))   

    def post_append_trigger(self, symbol: str, batch: bool = False) -> None:
        emit_window = pd.Timedelta(self.get_exchange_consumer_period_duration())
        if not batch and not self.check_df_contains_processors_window(self.symbol_df_dict[symbol], emit_window):
            self.logger.debug(f"post_append_trigger: not enough data for {symbol}:kline, post_append_trigger will not be called")
            event = self.fill_historical(symbol)
            if event is not None:
                self.primary.on_next(event)
            return None
        else:
            super().publish(symbol, KlineWindowDataEvent, emit_window)
            # direct std data to primary stream
            self.publish_std_data(symbol)
             
                
