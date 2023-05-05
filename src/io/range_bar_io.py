
import pandas as pd
from src.io.abstract_io import AbstractIO
from src.rx.scheduler import observe_on_scheduler
from src.strategies.rb_strategy.rb_strategy_indicators import RbStrategyIndicators
from src.util import get_logger
from rx.subject import Subject  # type: ignore
import rx.operators as op
from src.helpers.dataclasses import RangeBarIOCmdEvent, RangeBarWindowDataEvent, StrategyNextNonStdDataEvent
from src.io.enum_io import RigDataFrame
from datetime import datetime as dt, timedelta as td


class RangeBarIO(AbstractIO):

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

    def check_df_contains_processors_window(self, df: pd.DataFrame, window: pd.Timedelta | int) -> bool:
        bars = len(df)
        self.logger.info(f'check_df_contains_window_period: num of bar: {bars} >= {RbStrategyIndicators().get_indicators_min_window_size()}')    
        return bars >= RbStrategyIndicators().get_indicators_min_window_size()    

    def post_append_trigger(self, symbol: str, batch: bool = False) -> None:
        min_window = RbStrategyIndicators().get_indicators_min_window_size()
        super().publish(symbol, StrategyNextNonStdDataEvent, min_window)    
