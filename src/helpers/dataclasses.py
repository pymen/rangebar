from dataclasses import dataclass
import pandas as pd

@dataclass
class KlineWindowDataEvent:
    symbol: str
    df: pd.DataFrame

@dataclass
class RangeBarWindowDataEvent:
    symbol: str
    df: pd.DataFrame    

@dataclass
class RangeBarFrameIOCommandEvent:
    symbol: str
    df: pd.DataFrame

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
    payload: dict[str, str | int]

@dataclass
class KlineFrameIOCommandEvent:
    method: str
    df_name: str
    kwargs: dict[str, str | int]
        
        