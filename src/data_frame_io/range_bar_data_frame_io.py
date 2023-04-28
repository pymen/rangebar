from src.data_frame_io.abstract_data_frame_io import AbstractDataFrameIO
from src.helpers.util import get_strategy_parameters_max
from src.rx.pool_scheduler import observe_on_pool_scheduler
from src.strategies.simple_strategy.simple_strategy_indicators import SimpleStrategyIndicators
from src.util import get_logger
from rx.subject import Subject # type: ignore
import rx.operators as op
from src.helpers.dataclasses import KlineWindowDataEvent, RangeBarFrameIOCommandEvent, RangeBarWindowDataEvent

class RangeBarDataFrameIO(AbstractDataFrameIO):
    """
    In order for the indicators to be applied we need to have enough range bars to handle their look back periods.
    We can't fetch historical, but we can generate range bars from the kline data.
    That will happen on bot start up. But thereafter we are going to be creating a singe range bar at a time, 
    based on the latest kline & then publishing a df window for the indicators to be applied. With that latest new 
    range bar as the last row.
    So it will be the latest created + eg: 26 from storage or the number to make up the difference in this case a total
    of 27 
    """
    # this is the min window size of range bars that can be published to the indicators class eg: 26
    min_range_bar_window = get_strategy_parameters_max(SimpleStrategyIndicators)

    def __init__(self, df_name: str, primary: Subject) -> None:
        super().__init__(df_name, primary)
        self.logger = get_logger(f'RangeBarDataFrameIO')
        

    def init_subscriptions(self) -> None:
        super().init_subscriptions()
        self.primary.pipe( # type: ignore
                op.filter(lambda o: isinstance(o, RangeBarFrameIOCommandEvent)), # type: ignore
                op.map(lambda e: getattr(self, e.method)(**e.kwargs)), # type: ignore
                # observe_on_pool_scheduler()
            ).subscribe() 
    
    def publish_df_window(self, symbol: str) -> None:
        super().generic_publish_df_window(symbol, RangeBarWindowDataEvent, False)
 
    def append_post_processing(self, symbol: str) -> None:
        self.append_symbol_df_data_to_csv(symbol)
        self.publish_df_window(symbol)
            



