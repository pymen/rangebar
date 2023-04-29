
import pandas as pd
from src.io.abstract_io import AbstractIO
from src.helpers.util import get_strategy_parameters_max
from src.rx.scheduler import observe_on_scheduler
from src.strategies.simple_strategy.simple_strategy_indicators import SimpleStrategyIndicators
from src.util import get_logger
from rx.subject import Subject  # type: ignore
import rx.operators as op
from src.helpers.dataclasses import RangeBarIOCmdEvent, RangeBarWindowDataEvent, StrategyNextDataEvent
from src.io.enum_io import RigDataFrame
from datetime import datetime as dt, timedelta as td


class RangeBarIO(AbstractIO):
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
    min_range_bar_window = get_strategy_parameters_max(SimpleStrategyIndicators) * 3

    def __init__(self, primary: Subject) -> None:
        super().__init__(RigDataFrame.RANGE_BAR, primary)
        self.logger = get_logger(self)

    def init_subscriptions(self) -> None:
        self.primary.pipe(  # type: ignore
            op.filter(lambda o: isinstance(
                o, RangeBarIOCmdEvent)),  # type: ignore
            # sanitize_numeric_columns_df(),  # type: ignore
            op.map(lambda e: getattr(self, e.method)
                   (**e.kwargs)),  # type: ignore
            observe_on_scheduler()
        ).subscribe()
        self.primary.pipe(  # type: ignore
            op.filter(lambda o: isinstance(
                o, StrategyNextDataEvent)),  # type: ignore
            # sanitize_numeric_columns_df(),  # type: ignore
            op.map(self.save_range_bars_with_indicators),  # type: ignore
            observe_on_scheduler()
        ).subscribe()

    def save_range_bars_with_indicators(self, e: StrategyNextDataEvent):
        try:
            self.storage.save_symbol_df_data(
                e.symbol, 'range_bars_with_indicators', e.df, True)
        except Exception as ex:
            self.logger.error(f'save_range_bars_with_indicators: {str(ex)}')

    def check_df_contains_processors_window(self, df: pd.DataFrame, window: pd.Timedelta | int) -> bool:
        bars = len(df)
        self.logger.info(f'check_df_contains_window_period: num of bar: {bars} >= {self.min_range_bar_window}')    
        return bars >= self.min_range_bar_window    

    def post_append_trigger(self, symbol: str, batch: bool = False) -> None:
        super().publish(symbol, RangeBarWindowDataEvent, self.min_range_bar_window, self.min_range_bar_window)    
