import datetime
import pandas as pd
from src.io.abstract_io import AbstractIO
from src.helpers.util import get_strategy_parameters_max
from src.rx.pool_scheduler import observe_on_pool_scheduler
from src.strategies.simple_strategy.simple_strategy_indicators import SimpleStrategyIndicators
from src.util import get_logger
from rx.subject import Subject # type: ignore
import rx.operators as op
from src.helpers.dataclasses import RangeBarIOCmdEvent, RangeBarWindowDataEvent, StrategyNextEvent
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
    min_range_bar_window = get_strategy_parameters_max(SimpleStrategyIndicators)

    def __init__(self, primary: Subject) -> None:
        super().__init__(RigDataFrame.RANGE_BAR, primary)
        self.logger = get_logger(self)
        
    def init_subscriptions(self) -> None:
        self.primary.pipe( # type: ignore
                op.filter(lambda o: isinstance(o, RangeBarIOCmdEvent)), # type: ignore
                op.map(lambda e: getattr(self, e.method)(**e.kwargs)), # type: ignore
                # observe_on_pool_scheduler()
            ).subscribe()
        self.primary.pipe( # type: ignore
                op.filter(lambda o: isinstance(o, StrategyNextEvent)), # type: ignore
                op.map(self.save_range_bars_with_indicators), # type: ignore
                # observe_on_pool_scheduler()
            ).subscribe()
        
    def save_range_bars_with_indicators(self, e: StrategyNextEvent):
        try:
            self.save_symbol_df_data(e.symbol, 'range_bars_with_indicators', e.df)
        except Exception as e:
            self.logger.error(f'save_range_bars_with_indicators: {str(e)}')
         
        
    def get_window_period_duration(self, symbol: str) -> pd.Timedelta | None:
        # Calculate the safe window period duration
        safe_window = pd.Timedelta(minutes=self.min_range_bar_window + 1)
        # Check whether the DataFrame has enough data to apply indicators
        df = self.symbol_df_dict[symbol]
        start = df.index[0]
        end = df.index[-1]
        if isinstance(start, datetime.datetime) and isinstance(end, datetime.datetime):
            timedelta_in_minutes = (end - start).total_seconds() / 60.0 # type: ignore
            # Return the period duration if the DataFrame has enough data, otherwise raise an error
            if timedelta_in_minutes >= safe_window.total_seconds() / 60.0:
                return safe_window
            else:
                raise ValueError(f'Not enough data to apply indicators. timedelta_in_minutes: {timedelta_in_minutes}, safe_window: {safe_window}')
        else:
            self.logger.error(f'start: {start}, end: {end}, df indexes are not datetime.datetime')
            return None    

    def append_post_processing(self, symbol: str) -> None:
        try:
            try:
                self.save_symbol_df_data(symbol)
            except Exception as e:
                self.logger.error(f'append_post_processing: save_symbol_df_data: {str(e)}')
            period_duration = self.get_window_period_duration(symbol)
            if period_duration is not None:
                super().generic_publish_df_window(symbol, RangeBarWindowDataEvent, period_duration)
        except ValueError as e:
            self.logger.warning(f'append_post_processing: {str(e)}')
            
            



