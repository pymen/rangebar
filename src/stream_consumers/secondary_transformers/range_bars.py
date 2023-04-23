import pandas as pd
import numpy as np
from src.helpers.dataclasses import HistoricalKlineEvent, KlineEvent
from src.helpers.decorators import consumer_source
from src.rx.pool_scheduler import observe_on_pool_scheduler
from src.stream_consumers.secondary_stream_consumer import SecondaryStreamConsumer
from src.util import get_logger
from rx.subject import Subject
from src.rx.pool_scheduler import observe_on_pool_scheduler
from src.util import get_logger
import rx.operators as op
import pandas as pd
from rx.subject import Subject


@consumer_source(event_source=KlineEvent)
class RangeBar(SecondaryStreamConsumer):
    """
    Need a reference to the window to access the data frames
    """

    def __init__(self, primary: Subject, secondary: Subject):
        super().__init__(primary, secondary)
        self.logger = get_logger('RangeBar')
        self.window.add_consumer(self)
        self.primary = primary
        self.secondary = secondary
        self.primary.pipe(
                op.filter(lambda o: isinstance(o, self.event_source)),
                op.map(self.process),
                observe_on_pool_scheduler(),
             ).subscribe()
        
    def process(self, e: KlineEvent):
        self.logger.info(f'process: {e}')
      
        return df    


    def create_range_bar_df(self, df_window: pd.DataFrame) -> pd.DataFrame:
        """
        the window is from the last range bar timestamp to now, a mechanism to pull historical kline 
        data to fill in a gap that may occur if the application is stopped is also provided via 
        src.fetch_historical
        """
        # output_str = io.StringIO()
        # df_window.to_csv(output_str)
        # csv_contents = output_str.getvalue()
        # write_to_tests_out_file(csv_contents, 'df_window.csv')
        
        range_bars = []
        current_bar = {'adv': df.iloc[0]['adv'], 'volume': df.iloc[0]['volume'], 'average_adr': df.iloc[0]['average_adr'], 'timestamp': df.index.to_series(
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
                    current_bar = {'timestamp': pd.Timestamp(index) + pd.Timedelta(seconds=(i + 1)), 'adv': row['adv'], 'volume': row['volume'], 'average_adr': row['average_adr'], 'open': current_low + range_size * (
                        i), 'high': current_low + range_size * (i + 1), 'low': current_low + range_size * (i), 'close': current_low + range_size * (i + 1)}
                    # print(f'adjusted timestamp: {current_bar["timestamp"]}')
                    filler_bars += 1
                    range_bars.append(current_bar)

                current_bar = {'volume': row['volume'] * num_bars, 'average_adr': row['average_adr'], 'adv': row['adv'], 'timestamp': index,
                               'open': current_low + range_size * num_bars, 'high': high, 'low': current_low + range_size * num_bars, 'close': row['close']}
                current_high = high
                current_low = current_bar['low']

            elif current_high - low >= range_size:
                current_bar['close'] = current_high - range_size
                range_bars.append(current_bar)

                num_bars = int((current_high - low - range_size) // range_size)
                for i in range(num_bars):
                    current_bar = {'timestamp': pd.Timestamp(index) + pd.Timedelta(seconds=(i + 1)), 'adv': row['adv'], 'volume': row['volume'], 'average_adr': row['average_adr'], 'open': current_high - range_size * (
                        i + 1), 'high': current_high - range_size * (i), 'low': current_high - range_size * (i + 1), 'close': current_high - range_size * (i + 1)}
                    # print(f'adjusted timestamp: {current_bar["timestamp"]}')
                    filler_bars += 1
                    range_bars.append(current_bar)

                current_bar = {'volume': row['volume'] * (num_bars + 1), 'average_adr': row['average_adr'], 'adv': row['adv'], 'timestamp': index,
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
                current_bar['adv'] = row['adv']
        self.logger.debug(f"create_range_bar_df: filler_bars: {filler_bars}")
        self.logger.debug(
            f"create_range_bar_df: range_bars: length: {str(range_bars)}")
        return pd.DataFrame(range_bars)

    
