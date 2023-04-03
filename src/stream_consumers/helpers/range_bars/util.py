
import pandas as pd
import numpy as np

def create_range_bar_df(df: pd.DataFrame, average_adr: float) -> pd.DataFrame:
        range_bars = []
        current_bar = {'average_adr': average_adr,'timestamp': df.index.to_series()[0], 'open': df.iloc[0]['open'], 'high': df.iloc[0]['high'], 'low': df.iloc[0]['low'], 'close': df.iloc[0]['close']}
        current_high = current_bar['high']
        current_low = current_bar['low']

        for index, row in df.iterrows():
            high = row['high']
            low = row['low']
            range_size = average_adr * 0.1

            if high - current_low >= range_size:
                current_bar['close'] = current_low + range_size
                range_bars.append(current_bar)

                num_bars = int((high - current_low - range_size) // range_size)
                for i in range(num_bars):
                    current_bar = {'average_adr': average_adr,'timestamp': index, 'open': current_low + range_size * (i), 'high': current_low + range_size * (i + 1), 'low': current_low + range_size * (i), 'close': current_low + range_size * (i + 1)}
                    range_bars.append(current_bar)

                current_bar = {'average_adr': average_adr,'timestamp': index, 'open': current_low + range_size * num_bars, 'high': high, 'low': current_low + range_size * num_bars, 'close': row['close']}
                current_high = high
                current_low = current_bar['low']

            elif current_high - low >= range_size:
                current_bar['close'] = current_high - range_size
                range_bars.append(current_bar)

                num_bars = int((current_high - low - range_size) // range_size)
                for i in range(num_bars):
                    current_bar = {'average_adr': average_adr,'timestamp': index, 'open': current_high - range_size * (i + 1), 'high': current_high - range_size * (i), 'low': current_high - range_size * (i + 2), 'close': current_high - range_size * (i + 1)}
                    range_bars.append(current_bar)

                current_bar = {'average_adr': average_adr,'timestamp': index, 'open': current_high - range_size * (num_bars + 1), 'high': current_high - range_size * num_bars, 'low': low, 'close': row['close']}
                current_high = current_bar['high']
                current_low = low
            else:
                current_high = max(current_high, high)
                current_low = min(current_low, low)
                current_bar['timestamp'] = index
                current_bar['high'] = current_high
                current_bar['low'] = current_low
                current_bar['close'] = row['close']
                current_bar['average_adr'] = average_adr

        return pd.DataFrame(range_bars)

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