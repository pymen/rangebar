from typing import Any
import numpy as np
import pandas as pd
from src.io.abstract_io import AbstractIO
from src.helpers.util import check_df_has_datetime_index
from src.util import get_logger
from rx.subject import Subject # type: ignore
from src.helpers.dataclasses import HistoricalKlineEvent, KlineWindowDataEvent
import datetime as dt
from src.helpers.dataclasses import KlineIOCmdEvent
import rx.operators as op
from src.io.enum_io import RigDataFrame

class KlineIO(AbstractIO):

    def __init__(self, primary: Subject) -> None:
        super().__init__(RigDataFrame.KLINE, primary)
        self.logger = get_logger(self)
        
  
    def init_subscriptions(self) -> None:
        self.primary.pipe( # type: ignore
            op.filter(lambda o: isinstance(o, KlineIOCmdEvent) and o.df_name == self.df_name), # type: ignore
            op.map(lambda e: getattr(self, e.method)(**e.kwargs)), # type: ignore
            # observe_on_pool_scheduler()
        ).subscribe()    

    def publish_df_window(self, symbol: str) -> None:
        super().generic_publish_df_window(symbol, KlineWindowDataEvent)
        
    def get_symbol_config(self, symbol: str) -> list[Any]:
        symbols_config = self.settings['symbols_config']
        return [d for d in symbols_config if d['symbol'] == symbol]

    def fill_historical(self, symbol: str) -> HistoricalKlineEvent | None:
        kline_df = self.symbol_df_dict[symbol]
        check_df_has_datetime_index(kline_df)
        kline_last_index: dt.datetime = kline_df.index[-1] # type: ignore
        kline_first_index: dt.datetime = kline_df.index[0] # type: ignore
        num_days = (kline_last_index - kline_first_index).days + 1
        self.logger.info(
            f"fill_historical: kline_last_index: {kline_last_index}, kline_first_index: {kline_first_index}, num_days: {num_days}")
        if num_days < self.settings['window']['value']:
            # Set last_timestamp to one month ago
            last_timestamp = pd.Timestamp.now() - pd.DateOffset(days=self.settings['window']['value'] + 1)
            event = HistoricalKlineEvent(
                symbol=symbol, source='kline', last_timestamp=last_timestamp)
            self.logger.info(f"fill_historical: event: {str(event)}")
            return event
        else:
            return None

    
    def add_basic_indicators(self, symbol: str) -> pd.DataFrame | None:
        try:
            df = self.symbol_df_dict[symbol]
            # ensure numeric columns are numeric
            cols_to_convert = [
                    'open', 'close', 'high', 'low', 'volume', 
                    'number_of_trades', 'quote_asset_volume', 
                    'taker_buy_asset_volume',
                    'taker_buy_quote_asset_volume', 
                    'average_adr',
                    'apv'
            ]
            df[cols_to_convert] = df[cols_to_convert].apply(lambda x: pd.to_numeric(x, errors='coerce'))
            df = self.apv(self.relative_adr_range_size(df))
            return df
        except Exception as e:
            self.logger.error(f"create_range_bar_df: {str(e)}")

    def adr(self, df: pd.DataFrame) -> float | None:
        df['date'] = df.copy().index.date  # type: ignore
        df[['high', 'low']] = df[['high', 'low']].fillna(0)   # type: ignore
        try:
            daily_high_low = df.groupby(  # type: ignore
                'date')[['high', 'low']].agg(['max', 'min']) # type: ignore
            self.logger.debug(f"adr: daily_high_low: {str(daily_high_low)}")  # type: ignore
            high_max: pd.Series = daily_high_low[('high', 'max')]
            low_min: pd.Series = daily_high_low[('low', 'min')]
            # convert the Series to numeric values
            high_max = pd.to_numeric(high_max, errors='coerce')
            low_min = pd.to_numeric(low_min, errors='coerce')
            self.logger.debug(f"adr: high_max: {high_max.to_list()} ({type(high_max)}),  low_min: {low_min.to_list()} ({type(low_min)})")  # type: ignore
            adr = high_max - low_min # type: ignore
            self.logger.debug(f"adr: vector subtraction: adr: {adr}")
            daily_high_low['adr'] = adr
            average_adr = np.mean(daily_high_low['adr']).item()  # type: ignore
            self.logger.info(f"result: adr: average_adr: {str(average_adr)}")  # type: ignore
            return average_adr
        except Exception as e:
            self.logger.error(f"adr: {str(e)}")
            return None

    def relative_adr_range_size(self, df_in: pd.DataFrame, resample_arg: str = 'W') -> pd.DataFrame:
        groups = df_in.resample(resample_arg) # type: ignore
        df_out = pd.DataFrame()
        for _, group in groups:
            week_day_seg = group.copy()
            average_adr = self.adr(week_day_seg)
            if average_adr is not None:
                week_day_seg['average_adr'] = average_adr
                df_out = pd.concat([df_out, week_day_seg]) # type: ignore
        return df_out
    
    def apv(self, df: pd.DataFrame, window: int=14) -> pd.DataFrame:
        result = df['volume'].rolling(window=window).mean() # type: ignore
        result.fillna(0, inplace=True)   # type: ignore
        df['apv'] = result
        return df
    
    def append_post_processing(self, symbol: str) -> None:
        event = self.fill_historical(symbol)
        if event is not None:
            self.primary.on_next(event)
        elif self.check_df_contains_window_period(self.symbol_df_dict[symbol]):
            df_with_basic_indicators = self.add_basic_indicators(symbol)
            if df_with_basic_indicators is not None:
                self.symbol_df_dict[symbol] = df_with_basic_indicators
                self.save_symbol_df_data(symbol)
                self.publish_df_window(symbol)
        
