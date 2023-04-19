from typing import Dict
import pandas as pd
import numpy as np
from src.helpers.dataclasses import FetchHistoricalEvent
from src.helpers.decorators import consumer_source, derived_frame_trigger
from src.stream_consumers.stream_consumer import StreamConsumer
from src.stream_consumers.transformers.kline import Kline
from src.window.window import Window

@consumer_source(name='kline')
class RangeBar(StreamConsumer):

    def __init__(self, window: Window):
        super().__init__(window, Kline.col_mapping, 'kline')
        super().subscribe({'interval': '1m'})

    # drop inter-min rows
    def transform_message_dict(self, input_dict) -> dict:
        input_dict["k"]["s"] = input_dict["s"]
        if input_dict["k"]["x"] == False:
            return None
        return input_dict["k"]

    @derived_frame_trigger(df_name="range_bars", count=1)
    def create_range_bars(self, df: pd.DataFrame, symbol: str = None) -> pd.DataFrame:
        # access existing range_bar_df and check timestamp of last row
        range_bar_df = self.window.symbol_dict_df_dict[symbol]["range_bars"]
        kline_df = self.window.symbol_dict_df_dict[symbol]["kline"]
        num_days = (kline_df.index[-1] - kline_df.index[0]).days + 1
        if not range_bar_df.empty:
            last_timestamp = range_bar_df.tail(1).index
            # Compare last_timestamp to current time and publish a fetch historical event if more than 1 minute has elapsed
            if (pd.Timestamp.now() - last_timestamp).seconds / 60 > 1:
                # this is for the purpose of pulling historical to fill a gap, created by app shutdown
                self.window.historical.on_next(FetchHistoricalEvent(symbol=symbol, source='kline', last_timestamp=last_timestamp))
                return None
        elif num_days < 30:
            # Set last_timestamp to one month ago
            last_timestamp = pd.Timestamp.now() - pd.DateOffset(months=1)
            self.window.historical.on_next(FetchHistoricalEvent(symbol=symbol, source='kline', last_timestamp=last_timestamp))
            return None   
        
        return self.create_range_bar_df(df)
    
    def create_range_bar_df(self, df_window: pd.DataFrame) -> pd.DataFrame:
        """
        the window is from the last range bar timestamp to now, a mechanism to pull historical kline 
        data to fill in a gap that may occur if the application is stopped is also provided via 
        src.fetch_historical
        """
        df = self.adv(self.relative_adr_range_size(df_window))
        range_bars = []
        current_bar = {'adv': df.iloc[0]['adv'], 'volume': df.iloc[0]['volume'], 'average_adr': df.iloc[0]['average_adr'], 'timestamp': df.index.to_series(
        )[0], 'Open': df.iloc[0]['Open'], 'High': df.iloc[0]['High'], 'Low': df.iloc[0]['Low'], 'Close': df.iloc[0]['Close']}
        current_high = current_bar['High']
        current_low = current_bar['Low']
        filler_bars = 0

        for index, row in df.iterrows():
            high = row['High']
            low = row['Low']
            range_size = row['average_adr'] * 0.1

            if high - current_low >= range_size:
                current_bar['Close'] = current_low + range_size
                range_bars.append(current_bar)

                num_bars = int((high - current_low - range_size) // range_size)
                for i in range(num_bars):
                    current_bar = {'timestamp': pd.Timestamp(index) + pd.Timedelta(seconds=(i + 1)), 'adv': row['adv'], 'volume': row['volume'], 'average_adr': row['average_adr'], 'Open': current_low + range_size * (
                        i), 'High': current_low + range_size * (i + 1), 'Low': current_low + range_size * (i), 'Close': current_low + range_size * (i + 1)}
                    # print(f'adjusted timestamp: {current_bar["timestamp"]}')
                    filler_bars += 1
                    range_bars.append(current_bar)

                current_bar = {'volume': row['volume'] * num_bars, 'average_adr': row['average_adr'], 'adv': row['adv'], 'timestamp': index,
                            'Open': current_low + range_size * num_bars, 'High': high, 'Low': current_low + range_size * num_bars, 'Close': row['Close']}
                current_high = high
                current_low = current_bar['Low']

            elif current_high - low >= range_size:
                current_bar['Close'] = current_high - range_size
                range_bars.append(current_bar)

                num_bars = int((current_high - low - range_size) // range_size)
                for i in range(num_bars):
                    current_bar = {'timestamp': pd.Timestamp(index) + pd.Timedelta(seconds=(i + 1)), 'adv': row['adv'], 'volume': row['volume'], 'average_adr': row['average_adr'], 'Open': current_high - range_size * (
                        i + 1), 'High': current_high - range_size * (i), 'Low': current_high - range_size * (i + 1), 'Close': current_high - range_size * (i + 1)}
                    # print(f'adjusted timestamp: {current_bar["timestamp"]}')
                    filler_bars += 1
                    range_bars.append(current_bar)

                current_bar = {'volume': row['volume'] * (num_bars + 1), 'average_adr': row['average_adr'], 'adv': row['adv'], 'timestamp': index,
                            'Open': current_high - range_size * (num_bars + 1), 'High': current_high - range_size * num_bars, 'Low': low, 'Close': row['Close']}
                current_high = current_bar['High']
                current_low = low
            else:
                current_high = max(current_high, high)
                current_low = min(current_low, low)
                current_bar['timestamp'] = index
                current_bar['High'] = current_high
                current_bar['Low'] = current_low
                current_bar['Close'] = row['Close']
                current_bar['average_adr'] = row['average_adr']
                current_bar['volume'] = row['volume']
                current_bar['adv'] = row['adv']

        return pd.DataFrame(range_bars), filler_bars


    def adr(self, df: pd.DataFrame) -> float:
        df['date'] = pd.to_datetime(df.copy()['timestamp']).dt.date
        daily_high_low = df.groupby('date')['high', 'low'].agg(['max', 'min'])
        daily_high_low['adr'] = daily_high_low[(
            'high', 'max')] - daily_high_low[('low', 'min')]
        return np.mean(daily_high_low['adr'])


    def relative_adr_range_size(self, df_in: pd.DataFrame, resample_arg: str = 'W'):
        groups = df_in.resample(resample_arg)
        df_out = pd.DataFrame()
        for _, group in groups:
            week_day_seg = group.copy()
            average_adr = self.adr(week_day_seg)
            week_day_seg['average_adr'] = average_adr
            df_out = pd.concat([df_out, week_day_seg])
        return df_out
    
    def adv(self, df: pd.DataFrame, window=14):
        result = df['volume'].rolling(window=window).mean()
        result.fillna(0, inplace=True)
        df['adv'] = result
        return df
        
        

