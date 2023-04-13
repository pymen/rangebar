from src.helpers.dataclasses import FetchHistoricalEvent
from src.stream_consumers.transformers.kline import Kline
from src.window.window import Window
import rx.operators as op
from binance.um_futures import UMFutures
import pandas as pd
import datetime



class HistoricalKline:

    transformer: Kline
    def __init__(self, window: Window):
         self.window = window
         self.transformer = Kline(window)
         window.historical.pipe(op.filter(lambda e: e.source == 'kline'), op.map(self.fetch_historical)).subscribe()
         self.um_futures_client = UMFutures()


    def fetch_historical(self, e: FetchHistoricalEvent):
        """
        Fetches historical kline from the last_timestamp in the event and calls
        window.append_rows function which will eval_triggers eg: in the case where
        a derived source such as range bars published the FetchHistoricalEvent the
        missing source data will be there for it to continue. The time elapsed may 
        need to be adjusted depending on how long this takes
        """
        from_time = datetime.datetime.now()
        last_timestamp = e.last_timestamp
        # um_futures_client.klines: limit: optional int; limit the results. Default 500, max 1000.
        # Get the difference in minutes between now and the last timestamp
        minutes = int((last_timestamp - from_time).total_seconds() / 60)     
        # Get the number of 1000 minute intervals
        intervals = int(minutes / 1000)
        # Get the remainder
        remainder = minutes % 1000
        # Create a list of pairs of start and end times
        pairs = []
        for i in range(intervals):
            start = last_timestamp - datetime.timedelta(minutes=1000)
            end = last_timestamp
            pairs.append([start.strftime('%Y-%m-%d %H:%M:%S'), end.strftime('%Y-%m-%d %H:%M:%S')])
            last_timestamp = start
        if remainder > 0:
            start = last_timestamp - datetime.timedelta(minutes=remainder)
            end = last_timestamp
            pairs.append([start.strftime('%Y-%m-%d %H:%M:%S'), end.strftime('%Y-%m-%d %H:%M:%S')])

        resp_data = []
        for pairs in pairs:
            start = self.get_unix_epoch_time_ms(pairs[0])
            end = self.get_unix_epoch_time_ms(pairs[1])
            resp = self.um_futures_client.klines(symbol=e.symbol, interval="1m", startTime=start, endTime=end)
            resp_data.extend(resp)  
        # Create an empty dataframe
        df = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'num_of_trades', 'taker_buy_base', 'taker_buy_quote'])

        # Loop through each item in resp and append to the dataframe
        for item in resp_data:
            timestamp, oopen, high, low, close, volume, close_time, quote_asset_volume, num_of_trades, taker_buy_base, taker_buy_quote, ignore = item
            # create a dictionary of the values
            data = {'timestamp': timestamp, 'open': oopen, 'high': high, 'low': low, 'close': close, 'volume': volume, 'close_time': close_time, 'quote_asset_volume': quote_asset_volume, 'num_of_trades': num_of_trades, 'taker_buy_base': taker_buy_base, 'taker_buy_quote': taker_buy_quote}
            # append the dictionary as a row to the dataframe
            df = pd.concat([df, pd.DataFrame(data, index=[timestamp])])

        # Set timestamp as the index
        # convert timestamp column to datetime and set it as index
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        self.window.append_rows(e.symbol, 'kline', df)
        return df

    def get_unix_epoch_time_ms(self, datetime_str):
        datetime_obj = datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        unix_epoch_time_ms = int(datetime_obj.timestamp() * 1000)
        return unix_epoch_time_ms 
                     