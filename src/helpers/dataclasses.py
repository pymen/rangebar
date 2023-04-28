from dataclasses import dataclass
import pandas as pd

@dataclass
class DataEvent:
   df: pd.DataFrame

@dataclass
class KlineWindowDataEvent(DataEvent):
    symbol: str
    

@dataclass
class RangeBarWindowDataEvent(DataEvent):
    symbol: str


@dataclass
class StrategyNextDataEvent(DataEvent):
    symbol: str   

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
class CmdEvent:
    kwargs: dict[str, str | int | pd.DataFrame] 

@dataclass
class KlineIOCmdEvent(CmdEvent):
    method: str
    df_name: str
    
@dataclass
class RangeBarIOCmdEvent(CmdEvent):
    method: str
    df_name: str

        
        