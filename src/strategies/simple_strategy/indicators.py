from typing import Tuple
import pandas as pd
import ta
from rx.subject import Subject
import rx.operators as op
from src.helpers.dataclasses import IndicatorTickEvent, StrategyTickEvent
from src.rx.pool_scheduler import observe_on_pool_scheduler


class SimpleStrategyIndicators:
    """
    The indicators are calculated every time a range bar is created & it's decision time based on the indicator set.
    The only reason we add them to the in-memory df is for record purposes. Since the df is written to disk when rows
    are outside the desired window.
    Depending on the indicator windows needed for this strategy, we can also determine the size of the window
    """

    def __init__(self, main: Subject):
        self.main = main

    def init_subscriptions(self):
        self.main.pipe(
            observe_on_pool_scheduler(),
            op.filter(lambda o: isinstance(o, IndicatorTickEvent)),
            op.map(self.apply)
        ).subscribe()

    def macd(self):
        macd = ta.trend.MACD(
            self.df['close'], window_slow=26, window_fast=12, window_sign=9)
        self.df['macd'] = macd.macd()
        self.df['macd_signal'] = macd.macd_signal()
        self.df['macd_histogram'] = macd.macd_diff()

    def bb(self):
        bb = ta.volatility.BollingerBands(
            self.df['close'], window=12, window_dev=2)
        self.df['bb_upper'] = bb.bollinger_hband()
        self.df['bb_lower'] = bb.bollinger_lband()

    def rsi(self):
        rsi = ta.momentum.RSIIndicator(self.df['close'], window=14)
        self.df['rsi'] = rsi.rsi()

    def apply(self, event: IndicatorTickEvent) -> Tuple[pd.DataFrame, int]:
        self.df = event.df.copy()
        self.macd()
        self.bb()
        self.rsi()
        self.main.on_next(StrategyTickEvent(event.symbol, self.df))
