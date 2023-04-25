from typing import Dict, List
import pandas as pd
import datetime as dt
import os
from src.rx.pool_scheduler import observe_on_pool_scheduler
from src.settings import get_settings
from src.util import get_file_path, get_logger
from rx.subject import Subject
import rx.operators as op
from src.helpers.dataclasses import DataFrameIOCommandEvent
from abc import ABC


class DataFrameIO(ABC):

    symbol_df_dict: Dict[str, pd.DataFrame] = {}

    def __init__(self, df_name: str, primary: Subject, secondary: Subject):
        super().__init__()
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
            op.filter(lambda o: isinstance(o, DataFrameIOCommandEvent) and o.df_name == self.df_name),
            op.map(lambda e: getattr(self, e.method)(**e.kwargs)),
            # observe_on_pool_scheduler()
        ).subscribe()
        
    def publish_df_window(self, symbol: str, event_object: object, primary: bool = True):
        df = self.symbol_df_dict[symbol]
        rolling_window = df.rolling(window=f"{self.settings['window']}")
        if rolling_window.has_valid_values():
            window_start = rolling_window.start_time[0]
            window_df = df[window_start:]
            if primary:
                self.primary.on_next(event_object(symbol, window_df))
            else:    
                self.secondary.on_next(event_object(symbol, window_df))

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

    def prune_symbol_df_window(self, symbol: str, df: pd.DataFrame):
        """
        Reduce size of in memory df, since we are only interested in 7 days
        """
        rolling_window = df.rolling(window=f"{self.settings['window']}")
        if rolling_window.has_valid_values():
            window_start = rolling_window.start_time[0]
            df = df[window_start:]
            self.symbol_df_dict[symbol] = rolling_window

    def save_symbol_df_data(self, symbol: str = None):
        df = self.symbol_df_dict[symbol]
        if not df.empty:
            df.to_csv(self.get_symbol_window_csv_path(
                        symbol, self.df_name))
            
    def append_symbol_df_data(self, symbol: str = None):
        df = self.symbol_df_dict[symbol]
        if not df.empty:
            df.to_csv(self.get_symbol_window_csv_path(
                        symbol, self.df_name), mode='a', header=False)        
               
    def get_symbol_window_csv_path(self, symbol: str, df_name: str) -> str:
        return get_file_path(f'symbol_windows/{symbol}-{df_name}.csv')

    def append_row(self, symbol: str = None, row: pd.Series = None):
        self.symbol_df_dict.setdefault(symbol, pd.DataFrame())
        row['timestamp'] = pd.to_datetime(row['timestamp'], unit='ms')
        row_as_frame = row.to_frame().T
        row_as_frame.set_index('timestamp', inplace=True)
        self.symbol_df_dict[symbol] = pd.concat(
            [self.symbol_df_dict[symbol], row_as_frame])
        self.append_post_processing(symbol)

    def append_rows(self, symbol: str, df_section: pd.DataFrame):
        self.symbol_df_dict.setdefault(symbol, pd.DataFrame())
        self.symbol_df_dict[symbol] = pd.concat(
            [self.symbol_df_dict[symbol], df_section])
        self.symbol_df_dict[symbol].sort_values('timestamp', inplace=True)
        self.symbol_df_dict[symbol].set_index('timestamp', inplace=True)
        self.append_post_processing(symbol)
        
    def get_symbol_config(self, symbol: str):
        symbols_config = self.settings['symbols_config']
        return [d for d in symbols_config if d['symbol'] == symbol]
    
    def add_basic_indicators(self, symbol: str = None):
        """
        Abstract method to be implemented by child classes
        """
        pass

    def fill_historical(self, symbol: str = None) -> bool:
        """
        Abstract method to be implemented by child classes
        """
        pass
    
    def append_post_processing(self, symbol: str):
        """
        Abstract method to be implemented by child classes
        """
        pass
