
import numpy as np
import pandas as pd
from src.data_frame_io.data_frame_io import DataFrameIO
from src.util import get_logger
from rx.subject import Subject
from src.helpers.dataclasses import HistoricalKlineEvent, PrimaryDataEvent

class KlineDataFrameIO(DataFrameIO):

    def __init__(self, df_name: str, primary: Subject, secondary: Subject):
        super().__init__(df_name, primary, secondary)
        self.logger = get_logger(f'PrimaryDataFrameIO_{df_name}')
        self.init_subscriptions()

    def publish_df_window(self, symbol: str):
        super().publish_df_window(symbol, PrimaryDataEvent, True)
        
    def get_symbol_config(self, symbol: str):
        symbols_config = self.settings['symbols_config']
        return [d for d in symbols_config if d['symbol'] == symbol]

    def fill_historical(self, symbol: str = None) -> bool:
        kline_df = self.symbol_df_dict[symbol]
        kline_last_index = kline_df.index[-1]
        kline_first_index = kline_df.index[0]
        num_days = (kline_last_index - kline_first_index).days + 1
        self.logger.info(
            f"fill_historical: kline_last_index: {kline_last_index}, kline_first_index: {kline_first_index}, num_days: {num_days}")
        if num_days < 7:
            # Set last_timestamp to one month ago
            last_timestamp = pd.Timestamp.now() - pd.DateOffset(months=1)
            event = HistoricalKlineEvent(
                symbol=symbol, source='kline', last_timestamp=last_timestamp)
            self.logger.info(f"fill_historical: event: {str(event)}")
            self.primary.on_next(event)
            return False
        else:
            return True

    def add_basic_indicators(self, symbol: str = None):
        try:
            df = self.symbol_df_dict[symbol]
            df = self.adv(self.relative_adr_range_size(df))
            return df
        except Exception as e:
            self.logger.error(f"create_range_bar_df: {str(e)}")

    def adr(self, df: pd.DataFrame) -> float:
        df['date'] = df.copy().index.date
        try:
            daily_high_low = df.groupby(
                'date')['high', 'low'].agg(['max', 'min'])
            self.logger.debug(f"adr: daily_high_low: {str(daily_high_low)}")
            daily_high_low['adr'] = daily_high_low[(
                'high', 'max')] - daily_high_low[('low', 'min')]
            return np.mean(daily_high_low['adr'])
        except Exception as e:
            self.logger.error(f"adr: {str(e)}")
        return None

    def relative_adr_range_size(self, df_in: pd.DataFrame, resample_arg: str = 'W'):
        groups = df_in.resample(resample_arg)
        df_out = pd.DataFrame()
        for _, group in groups:
            week_day_seg = group.copy()
            average_adr = self.adr(week_day_seg)
            if average_adr is not None:
                week_day_seg['average_adr'] = average_adr
                df_out = pd.concat([df_out, week_day_seg])
        return df_out

    def adv(self, df: pd.DataFrame, window=14):
        result = df['volume'].rolling(window=window).mean()
        result.fillna(0, inplace=True)
        df['adv'] = result
        return df
    
    def append_post_processing(self, symbol: str):
        self.add_basic_indicators(symbol)
        self.append_symbol_df_data(symbol)
        if self.fill_historical(symbol):
            self.publish_df_window(symbol)
