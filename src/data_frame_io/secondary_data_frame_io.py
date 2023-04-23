from src.data_frame_io.data_frame_io import DataFrameIO
from src.util import get_logger
from rx.subject import Subject
from src.helpers.dataclasses import SecondaryDataEvent

class SecondaryDataFrameIO(DataFrameIO):

    def __init__(self, df_name: str, primary: Subject, secondary: Subject):
        super().__init__(df_name, primary, secondary)
        self.logger = get_logger(f'SecondaryDataFrameIO{df_name}')
    
    def publish_df_window(self, symbol: str):
        super().publish_df_window(symbol, SecondaryDataEvent, False)
 
    def append_post_processing(self, symbol: str):
        self.append_symbol_df_data(symbol)
        self.publish_df_window(symbol)
            



