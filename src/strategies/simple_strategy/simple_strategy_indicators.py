from typing import Callable, Tuple
import pandas as pd
import ta
from src.strategies.abstract_strategy_indicators import AbstractStrategyIndicators


class SimpleStrategyIndicators(AbstractStrategyIndicators):
    """
    The indicators are calculated every time a range bar is created & it's decision time based on the indicator set.
    The only reason we add them to the in-memory df is for record purposes. Since the df is written to disk when rows
    are outside the desired window.
    Depending on the indicator windows needed for this strategy, we can also determine the size of the window
    """
    p_macd_window_slow=26
    p_macd_window_fast=12
    p_macd_window_sign=9
    p_bb_window=12
    p_bb_window_dev=2
    p_rsi_window=14

    
    def macd(self, df: pd.DataFrame) -> pd.DataFrame:
        macd = ta.trend.MACD( # type: ignore
            df['close'], window_slow=self.p_macd_window_slow, window_fast=self.p_macd_window_fast, window_sign=self.p_macd_window_sign, fillna=True)
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_histogram'] = macd.macd_diff()
        return df

    def bb(self, df: pd.DataFrame) -> pd.DataFrame:
        bb = ta.volatility.BollingerBands( # type: ignore
            df['close'], window=self.p_bb_window, window_dev=self.p_bb_window_dev)
        df['bb_upper'] = bb.bollinger_hband()
        df['bb_lower'] = bb.bollinger_lband()
        return df

    def rsi(self, df: pd.DataFrame) -> pd.DataFrame:
        rsi = ta.momentum.RSIIndicator(df['close'], window=self.p_rsi_window) # type: ignore
        df['rsi'] = rsi.rsi()
        return df
    
    def get_processors(self) -> list[Callable[[pd.DataFrame], pd.DataFrame]]:
        return [self.macd, self.bb, self.rsi]

    
