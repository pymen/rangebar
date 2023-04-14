from dataclasses import dataclass
import pandas as pd

@dataclass
class Event:
    path: str
    df: pd.DataFrame
    window: int

@dataclass
class FetchHistoricalEvent:
    symbol: str
    source: str
    last_timestamp: pd.Timestamp
        