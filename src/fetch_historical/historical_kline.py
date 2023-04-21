from src.helpers.dataclasses import FetchHistoricalEvent
from src.helpers.util import get_unix_epoch_time_ms
from src.rx.pool_scheduler import observe_on_pool_scheduler
from src.util import get_logger
from src.window.window import Window
import rx.operators as op
from binance.um_futures import UMFutures
import pandas as pd
import datetime

from rx.subject import Subject


class HistoricalKline:

   
    def __init__(self, window: Window, historical: Subject):
         self.window = window
         self.historical = historical
         self.processing = False
         self.historical.pipe(observe_on_pool_scheduler(), op.map(self.fetch_historical)).subscribe()
         self.um_futures_client = UMFutures()
         self.logger = get_logger('HistoricalKline')

    def fetch_historical(self, e: FetchHistoricalEvent):
        print(f'fetch_historical: e.type: {type(e)}, e: {str(e)}')
        if not self.processing:
            self.processing = True
            """
            Fetches historical kline from the last_timestamp in the event and calls
            window.append_rows function which will eval_triggers eg: in the case where
            a derived source such as range bars published the FetchHistoricalEvent the
            missing source data will be there for it to continue. The time elapsed may 
            need to be adjusted depending on how long this takes
            """
            pairs = self.get_1000_minute_intervals(e.last_timestamp)
            resp_data = self.fetch_all_intervals(e, pairs)
            df = self.build_df(resp_data, e.symbol)
            self.window.append_rows(e.symbol, 'kline', df)
            self.processing = False     


    def get_1000_minute_intervals(self, last_timestamp: pd.Timestamp):
        """
        Returns a list of pairs of start and end times
        """
        to_time_now = datetime.datetime.now() 
        minutes = int((to_time_now - last_timestamp).total_seconds() / 60)
        self.logger.info(f'minutes: {minutes}')
        intervals = int(minutes / 1000)
        remainder = minutes % 1000
        if remainder > 0:
            intervals = intervals + (1 if intervals % 2 == 1 else 2)
        stamps = [to_time_now]
        for i in range(1, intervals):
            bound = to_time_now - datetime.timedelta(minutes=1000*i)
            stamps.append(bound)
        stamps = stamps[::-1]
        pairs = [[stamps[i], stamps[i+1]] for i in range(0, len(stamps) - 1)]
        self.logger.info(f'pair.len: {len(pairs)}')
        for pair in pairs:
            self.logger.info(f'{pair[0]} - {pair[1]}')
        return pairs      


    def fetch_all_intervals(self, e: FetchHistoricalEvent, pairs: list([datetime, datetime])):
        resp_data = []
        count = 0
        for pair in pairs:
            count = count + 1
            dt_s, dt_e = pair
            start = get_unix_epoch_time_ms(dt_s)
            end = get_unix_epoch_time_ms(dt_e)
            self.logger.info(f'request: {count}, start: {start} end: {end}')
            resp = self.um_futures_client.klines(symbol=e.symbol, interval="1m", startTime=start, endTime=end, limit=1000)
            self.logger.info(f'len: {len(resp)}')
            resp_data.extend(resp)
        return resp_data
    
    def build_df(self, resp_data, symbol: str):
        """
        https://binance-docs.github.io/apidocs/futures/en/#kline-candlestick-data
        [
            [
                1499040000000,      // Open time
                "0.01634790",       // Open
                "0.80000000",       // High
                "0.01575800",       // Low
                "0.01577100",       // Close
                "148976.11427815",  // Volume
                1499644799999,      // Close time
                "2434.19055334",    // Quote asset volume
                308,                // Number of trades
                "1756.87402397",    // Taker buy base asset volume
                "28.46694368",      // Taker buy quote asset volume
                "17928899.62484339" // Ignore.
            ]
        ]
        """
        # Create an empty dataframe
        df = pd.DataFrame(columns=['symbol', 'timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_asset_volume', 'taker_buy_quote_asset_volume'])
        # Loop through each item in resp and append to the dataframe
        count = 0
        for item in resp_data:
            count = count + 1
            timestamp, oopen, high, low, close, volume, close_time, quote_asset_volume, num_of_trades, taker_buy_base, taker_buy_quote, ignore = item
            # create a dictionary of the values
            data = {
                    'symbol': symbol,
                    'timestamp': timestamp, 
                    'open': oopen, 
                    'high': high, 
                    'low': low, 
                    'close': close, 
                    'volume': volume, 
                    'close_time': close_time, 
                    'quote_asset_volume': quote_asset_volume, 
                    'number_of_trades': num_of_trades, 
                    'taker_buy_asset_volume': taker_buy_base, 
                    'taker_buy_quote_asset_volume': taker_buy_quote
                    }
            # append the dictionary as a row to the dataframe
            df = pd.concat([df, pd.DataFrame(data, index=[timestamp])])
            if count % 1000 == 0:
                self.logger.info(f'progress count: {count}')
        # Set timestamp as the index
        # convert timestamp column to datetime and set it as index
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df
                     