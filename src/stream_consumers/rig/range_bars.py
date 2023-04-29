import pandas as pd
from src.helpers.dataclasses import KlineWindowDataEvent, RangeBarIOCmdEvent
from src.helpers.decorators import consumer_source
from src.helpers.util import check_df_has_datetime_index
from src.rx.scheduler import observe_on_scheduler
from src.strategies.simple_strategy.simple_strategy_indicators import SimpleStrategyIndicators
from src.stream_consumers.rig_stream_consumer import RigStreamConsumer
from src.util import get_logger
from rx.subject import Subject # type: ignore
from src.rx.scheduler import observe_on_scheduler
from src.util import get_logger
import rx.operators as op
import pandas as pd
from functools import reduce



@consumer_source(name='range_bars')
class RangeBar(RigStreamConsumer):
    """
    Needs to handle the following:
    - create range bars from a kline df
    - create the next range bar(s) from a the buffer & the latest kline row
    - publish the range bar(s) io, the duplicates will be filtered out by the storage
    """

    def __init__(self, primary: Subject) -> None:
        super().__init__(primary)
        self.logger = get_logger(self)
        self.primary = primary
        self.symbol_buffer_kline_df_dict: dict[str, pd.DataFrame] = {}
        self.ss_indicators = SimpleStrategyIndicators().get_processors()
        self.ss_min_window_size = SimpleStrategyIndicators().get_indicators_min_window_size()
        self.logger.info(f'RangeBar: ss_min_window_size: {self.ss_min_window_size}, ss_indicators: len: {len(self.ss_indicators)}')
        
        
        self.primary.pipe(
                op.filter(lambda o: isinstance(o, KlineWindowDataEvent)), # type: ignore
                op.map(self.process),
                observe_on_scheduler(),
             ).subscribe()
        
    def get_updated_buffer(self, e: KlineWindowDataEvent) -> pd.DataFrame:
        df_new = e.df.copy()
        if self.symbol_buffer_kline_df_dict[e.symbol] is not None:
           self.symbol_buffer_kline_df_dict[e.symbol] = pd.concat([self.symbol_buffer_kline_df_dict[e.symbol], df_new])
        else:
            self.symbol_buffer_kline_df_dict[e.symbol] = df_new
        # keep the buffer size to the max window size
        self.symbol_buffer_kline_df_dict[e.symbol] = self.symbol_buffer_kline_df_dict[e.symbol].iloc[-self.ss_min_window_size:]
        return self.symbol_buffer_kline_df_dict[e.symbol]       
        
    def process(self, e: KlineWindowDataEvent) -> None:
        self.logger.info(f'process: {e}')
        buffer = self.get_updated_buffer(e)
        range_bar_df = self.create_range_bar_df(buffer)
        if range_bar_df is not None:
            range_bar_df = reduce(lambda df, processor: processor(df), self.ss_indicators, range_bar_df)
            self.logger.debug(f'range bars created, to be published {len(range_bar_df)}, setting unprocessed_kline to None')
            self.primary.on_next(RangeBarIOCmdEvent(method='append_rows', df_name='range_bar', kwargs={'symbol': e.symbol, 'df_section': range_bar_df}))
        else:
            self.logger.debug(f'range bars not created, nothing to publish')    


    def create_range_bar_df(self, df: pd.DataFrame) -> pd.DataFrame | None:
        check_df_has_datetime_index(df)
        """
        the window is from the last range bar timestamp to now, a mechanism to pull historical kline 
        data to fill in a gap that may occur if the application is stopped is also provided via 
        src.fetch_historical.

        This method may more often then not be running with len(df) == 1, but that is ok, at startup it
        may run for more
        """
        
        range_bars = []
        current_bar = {'apv': df.iloc[0]['apv'], 'volume': df.iloc[0]['volume'], 'average_adr': df.iloc[0]['average_adr'], 'timestamp': df.index.to_series(
        )[0], 'open': df.iloc[0]['open'], 'high': df.iloc[0]['high'], 'low': df.iloc[0]['low'], 'close': df.iloc[0]['close']}
        current_high = current_bar['high']
        current_low = current_bar['low']
        filler_bars = 0

        for index, row in df.iterrows():
            high = row['high']
            low = row['low']
            range_size = row['average_adr'] * 0.1

            if high - current_low >= range_size:
                current_bar['close'] = current_low + range_size
                range_bars.append(current_bar)

                num_bars = int((high - current_low - range_size) // range_size)
                for i in range(num_bars):
                    current_bar = {'timestamp': pd.Timestamp(index) + pd.Timedelta(seconds=(i + 1)), 'apv': row['apv'], 'volume': row['volume'], 'average_adr': row['average_adr'], 'open': current_low + range_size * ( # type: ignore
                        i), 'high': current_low + range_size * (i + 1), 'low': current_low + range_size * (i), 'close': current_low + range_size * (i + 1)}
                    # print(f'adjusted timestamp: {current_bar["timestamp"]}')
                    filler_bars += 1
                    range_bars.append(current_bar)

                current_bar = {'volume': row['volume'] * num_bars, 'average_adr': row['average_adr'], 'apv': row['apv'], 'timestamp': index,
                               'open': current_low + range_size * num_bars, 'high': high, 'low': current_low + range_size * num_bars, 'close': row['close']}
                current_high = high
                current_low = current_bar['low']

            elif current_high - low >= range_size:
                current_bar['close'] = current_high - range_size
                range_bars.append(current_bar)

                num_bars = int((current_high - low - range_size) // range_size)
                for i in range(num_bars):
                    current_bar = {'timestamp': pd.Timestamp(index) + pd.Timedelta(seconds=(i + 1)), 'apv': row['apv'], 'volume': row['volume'], 'average_adr': row['average_adr'], 'open': current_high - range_size * ( # type: ignore
                        i + 1), 'high': current_high - range_size * (i), 'low': current_high - range_size * (i + 1), 'close': current_high - range_size * (i + 1)}
                    # print(f'adjusted timestamp: {current_bar["timestamp"]}')
                    filler_bars += 1
                    range_bars.append(current_bar)

                current_bar = {'volume': row['volume'] * (num_bars + 1), 'average_adr': row['average_adr'], 'apv': row['apv'], 'timestamp': index,
                               'open': current_high - range_size * (num_bars + 1), 'high': current_high - range_size * num_bars, 'low': low, 'close': row['close']}
                current_high = current_bar['high']
                current_low = low
            else:
                current_high = max(current_high, high)
                current_low = min(current_low, low)
                current_bar['timestamp'] = index
                current_bar['high'] = current_high
                current_bar['low'] = current_low
                current_bar['close'] = row['close']
                current_bar['average_adr'] = row['average_adr']
                current_bar['volume'] = row['volume']
                current_bar['apv'] = row['apv']
        self.logger.debug(f"create_range_bar_df: filler_bars: {filler_bars}")
        self.logger.debug(
            f"create_range_bar_df: range_bars: length: {len(range_bars)}")
        if len(range_bars) > 0:
            rb_df = pd.DataFrame(range_bars)
            rb_df['timestamp'] = pd.to_datetime(rb_df['timestamp'])
            rb_df.set_index('timestamp', inplace=True)
            return rb_df
        else:
            self.logger.debug(f"no range bars created")
            return None

    
