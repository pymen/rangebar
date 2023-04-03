from dataclasses import dataclass
import pandas as pd

@dataclass
class Event:
    path: str
    df: pd.DataFrame
    window: int