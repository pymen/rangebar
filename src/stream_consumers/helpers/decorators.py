
from typing import List


def derived_frame_trigger(df_name: str, interval: int = None, count: int = None):
    def decorator(func):
        func.interval = interval
        func.count = count
        func.df_name = df_name
        func.is_derived_consumer_trigger = True
        return func
    return decorator

def indicator_trigger(df_name: str, interval: int = None, count: int = None):
    def decorator(func):
        func.interval = interval
        func.count = count
        func.df_name = df_name
        func.is_indicator_trigger = True
        return func
    return decorator

def config(**kwargs):
    def decorator(func):
        for key, value in kwargs.items():
            setattr(func, key, value)
        func.is_config = True
        return func
    return decorator

def consumer_source(name: str, df_index: List[str] = None):
    def decorator(cls):
        cls.source_name = name
        cls.index_cols = df_index
        return cls
    return decorator