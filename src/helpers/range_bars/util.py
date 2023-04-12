
import pandas as pd
import numpy as np

def create_range_bar_df(df: pd.DataFrame, average_adr: float) -> pd.DataFrame:
        range_bars = []
        current_bar = {'volume': df.iloc[0]['volume'], 'average_adr': df.iloc[0]['average_adr'],'timestamp': df.index.to_series()[0], 'Open': df.iloc[0]['Open'], 'High': df.iloc[0]['High'], 'Low': df.iloc[0]['Low'], 'Close': df.iloc[0]['Close']}
        current_high = current_bar['High']
        current_low = current_bar['Low']
        filler_bars = 0

        for index, row in df.iterrows():
            high = row['High']
            low = row['Low']
            range_size = average_adr * 0.1

            if high - current_low >= range_size:
                current_bar['Close'] = current_low + range_size
                range_bars.append(current_bar)

                num_bars = int((high - current_low - range_size) // range_size)
                for i in range(num_bars):
                    current_bar = {'timestamp': pd.Timestamp(index) + pd.Timedelta(seconds=(i + 1)), 'volume': row['volume'], 'average_adr': average_adr, 'Open': current_low + range_size * (i), 'High': current_low + range_size * (i + 1), 'Low': current_low + range_size * (i), 'Close': current_low + range_size * (i + 1)}
                    # print(f'adjusted timestamp: {current_bar["timestamp"]}')
                    filler_bars += 1
                    range_bars.append(current_bar)

                current_bar = {'volume': row['volume'] * num_bars, 'average_adr': average_adr,'timestamp': index, 'Open': current_low + range_size * num_bars, 'High': high, 'Low': current_low + range_size * num_bars, 'Close': row['Close']}
                current_high = high
                current_low = current_bar['Low']

            elif current_high - low >= range_size:
                current_bar['Close'] = current_high - range_size
                range_bars.append(current_bar)

                num_bars = int((current_high - low - range_size) // range_size)
                for i in range(num_bars):
                    current_bar = {'timestamp': pd.Timestamp(index) + pd.Timedelta(seconds=(i + 1)), 'volume': row['volume'], 'average_adr': average_adr, 'Open': current_high - range_size * (i + 1), 'High': current_high - range_size * (i), 'Low': current_high - range_size * (i + 1), 'Close': current_high - range_size * (i + 1)}
                    # print(f'adjusted timestamp: {current_bar["timestamp"]}')
                    filler_bars += 1
                    range_bars.append(current_bar)

                current_bar = {'volume': row['volume'] * (num_bars + 1), 'average_adr': average_adr,'timestamp': index, 'Open': current_high - range_size * (num_bars + 1), 'High': current_high - range_size * num_bars, 'Low': low, 'Close': row['Close']}
                current_high = current_bar['High']
                current_low = low
            else:
                current_high = max(current_high, high)
                current_low = min(current_low, low)
                current_bar['timestamp'] = index
                current_bar['High'] = current_high
                current_bar['Low'] = current_low
                current_bar['Close'] = row['Close']
                current_bar['average_adr'] = average_adr
                current_bar['volume'] = row['volume']

        rb_df = pd.DataFrame(range_bars)
        rb_df['timestamp'] = pd.to_datetime(rb_df['timestamp'])
        rb_df.set_index('timestamp', inplace=True)
        rb_df.sort_index(inplace=True)
        return rb_df

def adr(df: pd.DataFrame) -> float:
    df['date'] = pd.to_datetime(df.copy()['timestamp']).dt.date 
    daily_high_low = df.groupby('date')['high', 'low'].agg(['max', 'min'])
    daily_high_low['adr'] = daily_high_low[('high', 'max')] - daily_high_low[('low', 'min')]
    return np.mean(daily_high_low['adr'])

def relative_adr_range_size(df_in: pd.DataFrame, resample_arg: str = 'W') -> str:
    groups = df_in.resample(resample_arg)
    df_out = pd.DataFrame()
    for _, group in groups:
        week_day_seg = group.copy()
        average_adr = adr(week_day_seg)
        week_day_seg['average_adr'] = average_adr
        df_out = pd.concat([df_out, week_day_seg])
    return df_out  