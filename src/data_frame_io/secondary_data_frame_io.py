from src.data_frame_io.data_frame_io import DataFrameIO
from src.rx.pool_scheduler import observe_on_pool_scheduler
from src.util import get_logger
from rx.subject import Subject
import rx.operators as op
from src.helpers.dataclasses import PrimaryDataEvent, SecondaryDataEvent

class SecondaryDataFrameIO(DataFrameIO):
    """
    In order for the indicators to be applied we need to have enough range bars to handle their look back periods.
    We can't fetch historical, but we can generate range bars from the kline data.
    That will happen on bot start up. But thereafter we are going to be creating a singe range bar at a time, 
    based on the latest kline & then publishing a df window for the indicators to be applied. With that latest new 
    range bar as the last row 
    """

    def __init__(self, df_name: str, primary: Subject, secondary: Subject):
        super().__init__(df_name, primary, secondary)
        self.logger = get_logger(f'SecondaryDataFrameIO{df_name}')

    def init_subscriptions(self):
        super().init_subscriptions()
        self.primary.pipe(
                op.filter(lambda o: isinstance(o, PrimaryDataEvent)),
                op.map(self.generate_range_bars),
                observe_on_pool_scheduler()
            ).subscribe() 
    
    def publish_df_window(self, symbol: str):
        super().publish_df_window(symbol, SecondaryDataEvent, False)
 
    def append_post_processing(self, symbol: str):
        self.append_symbol_df_data(symbol)
        self.publish_df_window(symbol)

    def generate_range_bars(self):
        pass    
            



