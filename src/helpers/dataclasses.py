from dataclasses import dataclass
import pandas as pd

@dataclass
class KlineEvent:
    symbol: str
    row: dict[str, str | int]

@dataclass
class RangeBarEvent:
    symbol: str
    df: pd.DataFrame # data frame with range bars for the symbol with len equal to what is needed by the indicator

@dataclass
class PrimaryDataEvent:
    symbol: str
    df: pd.DataFrame

@dataclass
class SecondaryDataEvent:
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
class DataFrameIOCommandEvent:
    method: str
    df_name: str
    kwargs: dict[str, str | int]
        
        