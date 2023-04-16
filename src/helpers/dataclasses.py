from dataclasses import dataclass
import pandas as pd

@dataclass
class Event:
    path: str
    df: pd.DataFrame
    window: int

@dataclass
class TickEvent:
    symbol: str
    df: pd.DataFrame  

@dataclass
class FetchHistoricalEvent:
    symbol: str
    source: str
    last_timestamp: pd.Timestamp

@dataclass
class OrderStatusEvent:
    symbol: str
    payload_type: str # 'http' or 'ws'
    payload: dict
        