from typing import Dict, List, Tuple
import asyncio
import numpy as np
import pandas as pd
import datetime as dt
import os
from src.rx.pool_scheduler import observe_on_pool_scheduler
from src.settings import get_settings
from src.util import get_file_path, get_logger
from rx.subject import Subject
import rx.operators as op
from src.helpers.dataclasses import HistoricalKlineEvent, DataFrameIOCommandEvent


class DataFrameIO:

    symbol_df_dict: Dict[str, pd.DataFrame] = {}
    prune_started = False

    def __init__(self, df_name: str, primary: Subject, secondary: Subject):
        self.logger = get_logger(f'DataFrameIO_{df_name}')
        self.df_name = df_name
        self.primary = primary
        self.secondary = secondary
        self.settings = get_settings('app')
        for symbols_config in self.settings['symbols_config']:
            df = self.load_symbol_df_window(symbols_config['symbol'])
            if bool(df):
                self.symbol_df_dict[symbols_config['symbol']] = df
            else:
                self.symbol_df_dict[symbols_config['symbol']] = {}

    def init_subscriptions(self):
        self.primary.pipe(
            op.filter(lambda o: isinstance(o, DataFrameIOCommandEvent)
                      and o.kwargs['df_name'] == self.df_name),
            op.map(lambda e: getattr(self, e.method)(**e.kwargs)),
            observe_on_pool_scheduler()
        ).subscribe()

    def load_symbol_df_window(self, symbol) -> pd.DataFrame:
        path = self.get_symbol_window_csv_path(symbol, self.df_name)
        if os.path.exists(path):
            df = pd.read_csv(path, index_col="timestamp", parse_dates=True)
            df.sort_index(inplace=True)
            # Convert last_window_end to a datetime object
            # dt.datetime.strptime(df.index[-1], "%Y-%m-%d %H:%M:%S.%f")
            last_window_end = df.index[-1]
            # dt.datetime.strptime(df.index[0], "%Y-%m-%d %H:%M:%S.%f")
            first_window_start = df.index[0]
            self.logger.info(
                f"last_window_end: {type(last_window_end)}, first_window_start: {type(first_window_start)}")
            # Convert integer to timedelta object
            window_timedelta = dt.timedelta(days=int(self.settings['window']))
            # Subtract timedelta from datetime object
            window_start = last_window_end - window_timedelta
            if window_start > first_window_start:
                df = df.loc[window_start:]
            return df

    def prune_df_windows(self):
        for symbols_config, df in self.symbol_df_dict.items():
            self.prune_symbol_df_window(symbols_config['symbol'], df)

    # FIXME: This is not working
    # Define a function named prune_symbol_window that takes in two arguments, symbol and df_dict
    def prune_symbol_df_window(self, symbol: str, df: pd.DataFrame):
        # Calculate the rolling window using the value of the current key
        rolling_window = df.rolling(window=f"{self.settings['window']}")
        # Check if the rolling window has valid values
        if rolling_window.has_valid_values():
            # Get the end time of the last window
            last_window_end = rolling_window.end_time[-1]
            # Get the data to drop from the start of the dataframe up to the last window end
            data_to_drop = df[:last_window_end]
            # Append the data to the CSV file
            data_to_drop.to_csv(self.get_symbol_window_csv_path(
                symbol, self.df_name), mode='a', header=False)
            # Remove the dropped data from the dataframe
            df = df[last_window_end:]
            # Update the symbol_dict_df_dict with the new rolling window
            self.symbol_df_dict[symbol] = rolling_window

    async def start_interval_save(self, delay_seconds=300):
        while True:
            await self.save_symbol_window_data()
            await asyncio.sleep(delay_seconds)

    def save_symbol_window_data(self):
        for symbol, df in self.symbol_df_dict.items():
            if not df.empty:
                df.to_csv(self.get_symbol_window_csv_path(
                    symbol, self.df_name))

    def get_symbol_window_csv_path(self, symbol: str, df_name: str) -> str:
        return get_file_path(f'symbol_windows/{symbol}-{df_name}.csv')

    def group_by_prefix(self, strings) -> List[List[str]]:
        groups = {}
        for string in strings:
            prefix = string.split('-')[0]
            if prefix not in groups:
                groups[prefix] = []
            groups[prefix].append(string)
        return groups

    # Define a function to append a row to a dataframe
    def append_row(self, symbol: str = None, row: pd.Series = None, index: List[str] = None):
        # Check if pruning has started and start the timer if not
        if not self.prune_started:
            self.prune_started = True
            # self.timer.start()
        # Create a dictionary of dataframes for each symbol and dataframe name
        self.symbol_df_dict.setdefault(symbol, pd.DataFrame())
        # Convert the timestamp to datetime format and set it as the index
        row['timestamp'] = pd.to_datetime(row['timestamp'], unit='ms')
        # Concatenate the new row with the existing dataframe and set the index to the timestamp
        row_as_frame = row.to_frame().T
        if index is None:
            row_as_frame.set_index('timestamp', inplace=True)
        else:
            row_as_frame.set_index(index, inplace=True)
        self.symbol_df_dict[symbol] = pd.concat(
            [self.symbol_df_dict[symbol], row_as_frame])

    # Define a function to append a historical df to the main df
    def append_rows(self, symbol: str, df_section: pd.DataFrame):
        # Check if pruning has started and start the timer if not
        if not self.prune_started:
            self.prune_started = True
            # self.timer.start()
        self.symbol_df_dict.setdefault(symbol, pd.DataFrame())
        self.symbol_df_dict[symbol] = pd.concat(
            [self.symbol_df_dict[symbol], df_section])
        self.symbol_df_dict[symbol].sort_values('timestamp', inplace=True)
        self.symbol_df_dict[symbol].set_index('timestamp', inplace=True)
        self.save_symbol_window_data()

    def get_symbol_config(self, symbol: str):
        symbols_config = self.settings['symbols_config']
        return [d for d in symbols_config if d['symbol'] == symbol]

    def fill_historical(self, df: pd.DataFrame, symbol: str = None) -> pd.DataFrame:
        """
        Only used for primary consumers.
        Currently only used for kline.
        """
        if self.df_name == 'kline':
            kline_df = self.window.symbol_df_dict[symbol]
            kline_last_index = kline_df.index[-1]
            kline_first_index = kline_df.index[0]
            num_days = (kline_last_index - kline_first_index).days + 1

            if num_days < 14:
                # Set last_timestamp to one month ago
                last_timestamp = pd.Timestamp.now() - pd.DateOffset(months=1)
                event = HistoricalKlineEvent(
                    symbol=symbol, source='kline', last_timestamp=last_timestamp)
                self.logger.info(f"fill_historical: event: {str(event)}")
                self.primary.on_next(event)
                return None
            self.logger.info(
                f"fill_historical: kline_last_index: {kline_last_index}, kline_first_index: {kline_first_index}, num_days: {num_days}")
            return self.add_basic_indicators(df, symbol)

    def add_basic_indicators(self, df: pd.DataFrame, symbol: str = None) -> Tuple(str, pd.DataFrame):
        try:
            df = self.adv(self.relative_adr_range_size(df))
            return symbol, df
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
