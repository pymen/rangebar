
import os
import pandas as pd
from src.io.enum_io import RigDataFrame
from src.util import get_file_path, get_logger, get_settings

class Storage:

    def __init__(self, rig_data_frame: RigDataFrame, symbol_df_dict: dict[str, pd.DataFrame]) -> None:
        self.logger = get_logger(self)
        self.settings = get_settings('app')
        self.df_name = rig_data_frame.value
        self.symbol_df_dict = symbol_df_dict

    def get_symbol_window_store_path(self, symbol: str, df_name: str) -> str:
        return str(get_file_path(f'symbol_windows/{symbol}-{df_name}.{self.settings["storage_ext"]}'))
        
    def restore_symbol_df_data(self, symbol: str) -> pd.DataFrame | None:
        path = self.get_symbol_window_store_path(symbol, self.df_name)
        self.logger.debug(f"restore_symbol_df_data: path: {path}")
        if os.path.exists(path):
            try:
                # Calculate the date for 7 days ago
                last_7_days = pd.Timestamp.now('UTC') - pd.Timedelta(days=7)
                # Load the entire dataframe from the pickle file
                restored_df = pd.read_pickle(path)
                # Remove duplicate rows with the same datetime index and keep only the last occurrence
                restored_df = restored_df[~restored_df.index.duplicated(keep='last')]
                # Slice the dataframe to keep only rows from the last 7 days
                restored_df = restored_df[last_7_days:]
                return restored_df
            except Exception as e:
                self.logger.error(f"Error restoring df: {e}")
                return None
            
    def save_symbol_df_data(self, symbol: str, name: str | None = None, df: pd.DataFrame | None = None) -> None:
        if name is None:
            name = self.df_name
        path = self.get_symbol_window_store_path(symbol, name)  # type: ignore
        self.logger.debug(f"save_symbol_df_data: path: {path}")
        if df is None:
            df = self.symbol_df_dict[symbol]
        if not df.empty:
            try:
                df_cp = df.copy()
                df_cp.to_pickle(path)
                # FIXME appending data will result in duplicated rows, would work if it was on shutdown only  
                # if os.path.exists(path):
                #     # Open the pickle file in append binary mode and append the new data
                #     with open(path, "ab") as f:
                #         df_cp.to_pickle(f)
                # else:        
                #     df_cp.to_pickle(path)     
            except Exception as e:
                self.logger.error(f"Error saving df: {e}")
                return None
                
               