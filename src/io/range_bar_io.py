import datetime
import pandas as pd
from typing import Any, Callable
from src.io.abstract_io import AbstractIO
from src.helpers.util import get_strategy_parameters_max
from src.rx.scheduler import observe_on_scheduler
from src.rx import sanitize_numeric_columns_df
from src.strategies.simple_strategy.simple_strategy_indicators import SimpleStrategyIndicators
from src.util import get_logger
from rx.subject import Subject  # type: ignore
import rx.operators as op
from src.helpers.dataclasses import RangeBarIOCmdEvent, RangeBarWindowDataEvent, StrategyNextDataEvent
from src.io.enum_io import RigDataFrame


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
    min_range_bar_window = get_strategy_parameters_max(
        SimpleStrategyIndicators)

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
            self.save_symbol_df_data(
                e.symbol, 'range_bars_with_indicators', e.df)
        except Exception as ex:
            self.logger.error(f'save_range_bars_with_indicators: {str(ex)}')

    def check_df_contains_processors_window(self, df: pd.DataFrame, window: pd.Timedelta | int) -> bool:
        start = df.index[0]
        end = df.index[-1]
        timedelta_in_minutes = (end - start).total_seconds() / 60.0 # type: ignore
        self.logger.info(f'check_df_contains_window_period: {timedelta_in_minutes} min >= {self.min_range_bar_window} min')    
        return timedelta_in_minutes >= self.min_range_bar_window    

    def post_append_trigger(self, symbol: str, batch: bool = False) -> None:
        processors_window = pd.Timedelta(minutes=self.min_range_bar_window + 1)
        emit_window = self.find_delta_for_last_mark(symbol)
        if batch:
            super().publish_batch_df_window(symbol, RangeBarWindowDataEvent, processors_window)
        else:    
            super().publish_df_window(symbol, RangeBarWindowDataEvent, processors_window, emit_window)
