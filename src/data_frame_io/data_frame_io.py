from typing import Any, Dict
import pandas as pd
import datetime as dt
import os
from src.helpers.util import check_df_has_datetime_index
# from src.rx.pool_scheduler import observe_on_pool_scheduler
from src.settings import get_settings
from src.util import get_file_path, get_logger
from rx.subject import Subject # type: ignore
import rx.operators as op # type: ignore
from src.helpers.dataclasses import DataFrameIOCommandEvent
from abc import ABC #, abstractmethod


class DataFrameIO(ABC):

    symbol_df_dict: Dict[str, pd.DataFrame] = {}

    def __init__(self, df_name: str, primary: Subject, secondary: Subject) -> None:
        super().__init__()
        self.logger = get_logger(f'DataFrameIO_{df_name}')
        self.df_name = df_name
        self.primary = primary
        self.secondary = secondary
        self.settings = get_settings('app')
        for symbols_config in self.settings['symbols_config']:
            # df = self.load_symbol_df_window(symbols_config['symbol'])
            df = None
            if bool(df):
                self.symbol_df_dict[symbols_config['symbol']] = df
            else:
                self.symbol_df_dict[symbols_config['symbol']] = pd.DataFrame()

    def get_period_duration(self) -> str:
        return f"{self.settings['window']['value']}{self.settings['window']['period_type']}"            

    def init_subscriptions(self) -> None:
        self.primary.pipe(
            op.filter(lambda o: isinstance(o, DataFrameIOCommandEvent) and o.df_name == self.df_name), # type: ignore
            op.map(lambda e: getattr(self, e.method)(**e.kwargs)), # type: ignore
            # observe_on_pool_scheduler()
        ).subscribe()
        
    def generic_publish_df_window(self, symbol: str, event_object: object, primary: bool = True) -> None:
        df = self.symbol_df_dict[symbol]
        rolling_window = df.rolling(window=self.get_period_duration())
        if rolling_window.has_valid_values(): # type: ignore
            window_start = rolling_window.start_time[0] # type: ignore
            window_df = df[window_start:]
            if primary:
                self.primary.on_next(event_object(symbol, window_df)) # type: ignore
            else:    
                self.secondary.on_next(event_object(symbol, window_df)) # type: ignore

    # def load_symbol_df_window(self, symbol: str) -> pd.DataFrame | None:
    #     path = self.get_symbol_window_csv_path(symbol, self.df_name)
    #     if os.path.exists(path):
    #         df = pd.read_csv(path, index_col="timestamp", parse_dates=True) # type: ignore
    #         df.sort_index(inplace=True) # type: ignore
           
    #         last_window_end: dt.datetime = df.index[-1] # type: ignore
          
    #         first_window_start: dt.datetime = df.index[0] # type: ignore
    #         self.logger.info(
    #             f"last_window_end: {type(last_window_end)}, first_window_start: {type(first_window_start)}")
    #         # Convert integer to timedelta object
    #         window_timedelta: dt.timedelta = dt.timedelta(days=int(self.settings['window']))
    #         # Subtract timedelta from datetime object
    #         window_start: dt.datetime = last_window_end - window_timedelta
    #         if window_start > first_window_start:
    #             df = df.loc[window_start:]
    #         return df

  

    def prune_symbol_df_window(self, symbol: str, df: pd.DataFrame) -> None: # type: ignore
        """
        Reduce size of in memory df, since we are only interested in 7 days
        """
        period_duration = self.get_period_duration()
        self.logger.debug(f"period_duration: {period_duration}")
        rolling_window = df.rolling(window=period_duration) # type: ignore
        if rolling_window.has_valid_values(): # type: ignore
            window_start: dt.datetime = rolling_window.start_time[0] # type: ignore
            df = df[window_start:] # type: ignore
            self.symbol_df_dict[symbol] = pd.DataFrame(rolling_window)

    def save_symbol_df_data(self, symbol: str) -> None:
        df = self.symbol_df_dict[symbol]
        if not df.empty:
            df.to_csv(self.get_symbol_window_csv_path(
                        symbol, self.df_name))
            
    def append_symbol_df_data(self, symbol: str) -> None:
        df = self.symbol_df_dict[symbol]
        if not df.empty:
            df.to_csv(self.get_symbol_window_csv_path(
                        symbol, self.df_name), mode='a', header=False)        
               
    def get_symbol_window_csv_path(self, symbol: str, df_name: str) -> str:
        return str(get_file_path(f'symbol_windows/{symbol}-{df_name}.csv'))
    
    def check_df_contains_window_period(self, df: pd.DataFrame) -> bool:
        check_df_has_datetime_index(df)
        """
        Check if a DataFrame with datetime index contains at least 7 days of data.
        
        :param df: Pandas DataFrame to check.
        :return: True if DataFrame contains at least 7 days of data, False otherwise.
        """
        window = self.settings['window']['value']
        # Get the range of dates covered by the DataFrame
        date_range = df.index.max() - df.index.min()
        # Check if the DataFrame covers at least 7 days
        if date_range.days >= window:
            return True
        else:
            self.logger.info(f"append_rows: DataFrame does not contain window period of data, yet")
            return False


    def append_row(self, symbol: str, row: Any) -> None:
        self.symbol_df_dict.setdefault(symbol, pd.DataFrame())
        row['timestamp'] = pd.to_datetime(row['timestamp'], unit='ms') # type: ignore
        row_as_frame = row.to_frame().T
        row_as_frame.set_index('timestamp', inplace=True)  # type: ignore
        self.symbol_df_dict[symbol] = pd.concat(  # type: ignore
            [self.symbol_df_dict[symbol], row_as_frame])
        self.append_post_processing(symbol)    

    def append_rows(self, symbol: str, df_section: pd.DataFrame) -> None:
        self.symbol_df_dict.setdefault(symbol, pd.DataFrame())
        self.symbol_df_dict[symbol] = pd.concat(  # type: ignore
            [self.symbol_df_dict[symbol], df_section])
        self.symbol_df_dict[symbol].sort_values('timestamp', inplace=True)  # type: ignore
        self.symbol_df_dict[symbol].set_index('timestamp', inplace=True)  # type: ignore
        self.append_post_processing(symbol)
            
        
    def get_symbol_config(self, symbol: str) -> list[Any]:
        symbols_config = self.settings['symbols_config']
        return [d for d in symbols_config if d['symbol'] == symbol]
    
    # @abstractmethod # forces the subclass to implement this method
    def add_basic_indicators(self, symbol: str) -> pd.DataFrame | None:
        """
        Abstract method to be implemented by child classes
        """
        pass

    # @abstractmethod # forces the subclass to implement this method
    def fill_historical(self, symbol: str) -> bool | None:
        """
        Abstract method to be implemented by child classes
        """
        pass
    
    # @abstractmethod # forces the subclass to implement this method
    def append_post_processing(self, symbol: str) -> None:
        """
        Abstract method to be implemented by child classes
        """
        pass
