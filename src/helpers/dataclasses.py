from dataclasses import dataclass
import pandas as pd

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
class WindowCommandEvent:
    method: str
    kwargs: dict
        
        