import pandas as pd

def create_range_bar_df(df: pd.DataFrame) -> pd.DataFrame:
    # Initialize an empty DataFrame with the same columns as df
    range_bars = pd.DataFrame(columns=df.columns)
    # Initialize variables for the first range bar
    range_open = df.iloc[0]['Close']
    range_high = df.iloc[0]['High']
    range_low = df.iloc[0]['Low']
    index_timestamp = df.index[0]
    # Carry over inactive columns
    volume = df.iloc[0]['volume'],
    date = df.iloc[0]['date'],
    average_adr = df.iloc[0]['average_adr'],
    adv = df.iloc[0]['adv']
    # Loop through the OLHC data and create the range bars
    for index, row in df.iterrows():
        timestamp = index

        # Calculate the range size based on the average ADR
        range_size = row['average_adr'] * 0.1

        # Check if a new range bar needs to be created
        if abs(row['High'] - range_open) >= range_size:
            # Calculate the close of the previous range bar
            range_close = df.loc[(index_timestamp, 'Close')]  # type: ignore
            # Add the previous range bar to the range_bars DataFrame
            prev_range_bar = pd.DataFrame({
                'Open': range_open,
                'High': range_high,
                'Low': range_low,
                'Close': range_close,
                'volume': volume,
                'date': date,
                'average_adr': average_adr,
                'adv': adv
            }, index=[index_timestamp])
            range_bars = pd.concat([range_bars, prev_range_bar])
            # Initialize variables for the new range bar
            range_open = df.loc[(index_timestamp, 'Close')]  # type: ignore
            range_high = row['High']
            range_low = row['Low']
            index_timestamp = timestamp
            # Carry over inactive columns
            volume = row['volume'],
            date = row['date'],
            average_adr = row['average_adr'],
            adv = row['adv']
        # Update the range_high and range_low variables
        else:
            range_high = max(range_high, row['High'])
            range_low = min(range_low, row['Low'])

    # Add the last range bar to the range_bars DataFrame
    range_close = df['Close'].iloc[-1]
    last_range_bar = pd.DataFrame({
        'Open': range_open,
        'High': range_high,
        'Low': range_low,
        'Close': range_close,
        'volume': volume,
        'date': date,
        'average_adr': average_adr,
        'adv': adv
    }, index=[index_timestamp])
    range_bars = pd.concat([range_bars, last_range_bar])
    return range_bars

def create_range_bar_df_erroneous(df: pd.DataFrame):
    range_bars = []
    current_bar = {'filler': 0, 'filler_seq': 0,  'adv': df.iloc[0]['adv'], 'volume': df.iloc[0]['volume'], 'average_adr': df.iloc[0]['average_adr'], 'timestamp': df.index.to_series(
    )[0], 'Open': df.iloc[0]['Open'], 'High': df.iloc[0]['High'], 'Low': df.iloc[0]['Low'], 'Close': df.iloc[0]['Close']}
    current_high = current_bar['High']
    current_low = current_bar['Low']
    filler_bars = 0

    for index, row in df.iterrows():
        idx: pd.Timestamp = index # type: ignore
        high = row['High']
        low = row['Low']
        range_size = row['average_adr'] * 0.1

        if high - current_low >= range_size:
            current_bar['Close'] = current_low + range_size
            range_bars.append(current_bar)

            num_bars = int((high - current_low - range_size) // range_size)
            for i in range(num_bars):
                current_bar = {'filler': 1, 'filler_seq': i, 'timestamp': idx + pd.Timedelta(seconds=(i + 1)), 'adv': row['adv'], 'volume': row['volume'], 'average_adr': row['average_adr'], 'Open': current_low + range_size * (
                    i), 'High': current_low + range_size * (i + 1), 'Low': current_low + range_size * (i), 'Close': current_low + range_size * (i + 1)}
                # print(f'adjusted timestamp: {current_bar["timestamp"]}')
                filler_bars += 1
                range_bars.append(current_bar)

            current_bar = {'filler': 0, 'filler_seq': 0, 'volume': row['volume'] * num_bars, 'average_adr': row['average_adr'], 'adv': row['adv'], 'timestamp': idx,
                           'Open': current_low + range_size * num_bars, 'High': high, 'Low': current_low + range_size * num_bars, 'Close': row['Close']}
            current_high = high
            current_low = current_bar['Low']

        elif current_high - low >= range_size:
            current_bar['Close'] = current_high - range_size
            range_bars.append(current_bar)

            num_bars = int((current_high - low - range_size) // range_size)
            for i in range(num_bars):
                current_bar = {'filler': 1, 'filler_seq': i, 'timestamp': idx + pd.Timedelta(seconds=(i + 1)), 'adv': row['adv'], 'volume': row['volume'], 'average_adr': row['average_adr'], 'Open': current_high - range_size * (
                    i + 1), 'High': current_high - range_size * (i), 'Low': current_high - range_size * (i + 1), 'Close': current_high - range_size * (i + 1)}
                # print(f'adjusted timestamp: {current_bar["timestamp"]}')
                filler_bars += 1
                range_bars.append(current_bar)

            current_bar = {'filler': 0, 'filler_seq': 0, 'volume': row['volume'] * (num_bars + 1), 'average_adr': row['average_adr'], 'adv': row['adv'], 'timestamp': idx,
                           'Open': current_high - range_size * (num_bars + 1), 'High': current_high - range_size * num_bars, 'Low': low, 'Close': row['Close']}
            current_high = current_bar['High']
            current_low = low
        else:
            current_high = max(current_high, high)
            current_low = min(current_low, low)
            current_bar['timestamp'] = idx
            current_bar['High'] = current_high
            current_bar['Low'] = current_low
            current_bar['filler'] = 0
            current_bar['filler_seq'] = 0
            current_bar['Close'] = row['Close']
            current_bar['average_adr'] = row['average_adr']
            current_bar['volume'] = row['volume']
            current_bar['adv'] = row['adv']

    return pd.DataFrame(range_bars), filler_bars

def create_range_bar_df2(df: pd.DataFrame) -> pd.DataFrame:
    # Initialize an empty DataFrame with the same columns as df
    range_bars = pd.DataFrame(columns=df.columns)
    # Initialize variables for the first range bar
    range_open = df.iloc[0]['Close']
    range_high = df.iloc[0]['High']
    range_low = df.iloc[0]['Low']
    index_timestamp = df.index[0]
    # Carry over inactive columns
    volume = df.iloc[0]['volume'],
    date = df.iloc[0]['date'],
    average_adr = df.iloc[0]['average_adr'],
    adv = df.iloc[0]['adv']
    # Loop through the OLHC data and create the range bars
    for index, row in df.iterrows():
        timestamp = index

        # Calculate the range size based on the average ADR
        range_size = row['average_adr'] * 0.1

        # Check if a new range bar needs to be created
        if abs(row['High'] - range_open) >= range_size:
            # Calculate the close of the previous range bar
            range_close = df.loc[(index_timestamp, 'Close')]  # type: ignore
            # Add the previous range bar to the range_bars DataFrame
            prev_range_bar = pd.DataFrame({
                'Open': range_open,
                'High': range_high,
                'Low': range_low,
                'Close': range_close,
                'volume': volume,
                'date': date,
                'average_adr': average_adr,
                'adv': adv
            }, index=[index_timestamp])
            range_bars = pd.concat([range_bars, prev_range_bar])
            # Initialize variables for the new range bar
            range_open = df.loc[(index_timestamp, 'Close')]  # type: ignore
            range_high = row['High']
            range_low = row['Low']
            index_timestamp = timestamp
            # Carry over inactive columns
            volume = row['volume'],
            date = row['date'],
            average_adr = row['average_adr'],
            adv = row['adv']
        # Update the range_high and range_low variables
        else:
            range_high = max(range_high, row['High'])
            range_low = min(range_low, row['Low'])

            if range_size > (high - current_low):
                num_bars = int((high - current_low - range_size) // range_size)
                for i in range(num_bars):
                    # Calculate the close of the previous range bar
                    range_close = current_low + range_size * (i + 1)
                    # Add the previous range bar to the range_bars DataFrame
                    prev_range_bar = pd.DataFrame({
                        'Open': current_low + range_size * i,
                        'High': current_low + range_size * (i + 1),
                        'Low': current_low + range_size * i,
                        'Close': range_close,
                        'volume': volume,
                        'date': date,
                        'average_adr': average_adr,
                        'adv': adv
                    }, index=[index_timestamp])
                    range_bars = pd.concat([range_bars, prev_range_bar])
                # Initialize variables for the new range bar
                range_open = current_low + range_size * num_bars
                range_high = high
                range_low = current_low + range_size * num_bars
                index_timestamp = timestamp
                # Carry over inactive columns
                volume = row['volume'] * num_bars,
                date = row['date'],
                average_adr = row['average_adr'],
                adv = row['adv']
                current_low = range_low

    # Add the last range bar to the range_bars DataFrame
    range_close = df['Close'].iloc[-1]
    last_range_bar = pd.DataFrame({
        'Open': range_open,
        'High': range_high,
        'Low': range_low,
        'Close': range_close,
        'volume': volume,
        'date': date,
        'average_adr': average_adr,
        'adv': adv
    }, index=[index_timestamp])
    range_bars = pd.concat([range_bars, last_range_bar])
    return range_bars

