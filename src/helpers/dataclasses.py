from dataclasses import dataclass
import pandas as pd

@dataclass
class KlineEvent:
    symbol: str
    row: dict

@dataclass
class RangeBarEvent:
    symbol: str
    df: pd.DataFrame # data frame with range bars for the symbol with len equal to what is needed by the indicator


@dataclass
class IndicatorTickEvent:
    symbol: str
    df: pd.DataFrame  

@dataclass
class StrategyTickEvent:
    symbol: str
    df: pd.DataFrame      

@dataclass
class HistoricalKlineEvent:
    symbol: str
    source: str
    last_timestamp: pd.Timestamp

@dataclass
class OrderStatusEvent:
    symbol: str
    payload_type: str # 'http' or 'ws'
    payload: dict

@dataclass
class DataFrameIOCommandEvent:
    method: str
    kwargs: dict
        
        