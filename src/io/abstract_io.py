from typing import Any, Dict
import pandas as pd
import datetime as dt
import os
from src.helpers.util import check_df_has_datetime_index
# from src.rx.pool_scheduler import observe_on_pool_scheduler
from src.util import get_file_path, get_logger, get_settings
from rx.subject import Subject # type: ignore
from abc import ABC, abstractmethod #, abstractmethod
from src.io.enum_io import RigDataFrame
from fastparquet import ParquetFile as pq_read, write as pq_write

class AbstractIO(ABC):

    symbol_df_dict: Dict[str, pd.DataFrame] = {}

    def __init__(self, rig_data_frame: RigDataFrame, primary: Subject) -> None:
        super().__init__()
        self.logger = get_logger(self)
        self.df_name = rig_data_frame.value
        self.primary = primary
        
        self.settings = get_settings('app')
        for symbols_config in self.settings['symbols_config']:
            # df = self.load_symbol_df_window(symbols_config['symbol'])
            df = None
            if bool(df):
                self.symbol_df_dict[symbols_config['symbol']] = df
            else:
                self.symbol_df_dict[symbols_config['symbol']] = pd.DataFrame()
        self.init_subscriptions()        

    def get_period_duration(self) -> str:
        return f"{self.settings['window']['value']}{self.settings['window']['period_type']}"            
 
    def generic_publish_df_window(self, symbol: str, event_object: object, period_duration: pd.Timedelta | None = None) -> None:
        if period_duration is None:
            period_duration = pd.Timedelta(self.get_period_duration()) 
        df = self.symbol_df_dict[symbol]
        window_df: pd.DataFrame = df.loc[df.index >= df.index.max() - period_duration]
        self.logger.debug(f"window_df: len: {len(window_df)}")
        has_correct_data = self.check_df_contains_window_period(window_df)
        if has_correct_data:
            self.primary.on_next(event_object(symbol, window_df)) # type: ignore
        else:
            self.logger.warning(f"Dataframe for {symbol} does not contain correct data")
                
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

    def save_symbol_df_data(self, symbol: str, name: str | None = None, df: pd.DataFrame | None = None) -> None:
        if name is None:
            name = self.df_name
        path = self.get_symbol_window_store_path(symbol, name) # type: ignore
        if df is None:
            df = self.symbol_df_dict[symbol]
        if not df.empty:
            df_cp = df.copy()
            df_cp.reset_index()
            df_cp.to_feather(path)
            
    def restore_symbol_df_data(self, symbol: str) -> None:
        path = self.get_symbol_window_store_path(symbol, self.df_name)
        if os.path.exists(path):
            restored_df = pd.read_feather(path)
            restored_df['timestamp'] = pd.to_datetime(restored_df['timestamp'])
            restored_df.set_index('timestamp', inplace=True)
            self.symbol_df_dict[symbol] = restored_df     
               
    def get_symbol_window_store_path(self, symbol: str, df_name: str) -> str:
        return str(get_file_path(f'symbol_windows/{symbol}-{df_name}.{self.settings["storage_ext"]}'))
    
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
        self.append_post_processing(symbol)
            
        
    def get_symbol_config(self, symbol: str) -> list[Any]:
        symbols_config = self.settings['symbols_config']
        return [d for d in symbols_config if d['symbol'] == symbol]
    
    # @abstractmethod # forces the subclass to implement this method - we want optional implementation
    def add_basic_indicators(self, symbol: str) -> pd.DataFrame | None:
        """
        Abstract method to be implemented by child classes
        """
        pass

    # @abstractmethod # forces the subclass to implement this method - we want optional implementation
    def fill_historical(self, symbol: str) -> bool | None:
        """
        Abstract method to be implemented by child classes
        """
        pass
    
    # @abstractmethod # forces the subclass to implement this method - we want optional implementation
    def append_post_processing(self, symbol: str) -> None:
        """
        Abstract method to be implemented by child classes
        """
        pass

    @abstractmethod    
    def init_subscriptions(self) -> None:
        pass
