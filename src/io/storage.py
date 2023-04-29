
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
        if os.path.exists(path):
            try:
                restored_df = pd.read_feather(path)
                restored_df['timestamp'] = pd.to_datetime(
                    restored_df['timestamp'])
                restored_df.set_index('timestamp', inplace=True)
                return restored_df
            except Exception as e:
                self.logger.error(f"Error restoring df: {e}")
                return None
            
    def save_symbol_df_data(self, symbol: str, name: str | None = None, df: pd.DataFrame | None = None) -> None:
        if name is None:
            name = self.df_name
        path = self.get_symbol_window_store_path(symbol, name)  # type: ignore
        if df is None:
            df = self.symbol_df_dict[symbol]
        if not df.empty:
            df_cp = df.copy()
            df_cp.reset_index(inplace=True)
            df_cp.to_feather(path, compression='lz4')        