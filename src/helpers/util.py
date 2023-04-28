
from datetime import datetime
from typing import Any
import pandas as pd


def get_unix_epoch_time_ms(dt: datetime = datetime.utcnow()) -> int:
    """Converts a datetime object to unix epoch time in milliseconds"""
    unix_epoch_time_ms = int(dt.timestamp() * 1000)
    return unix_epoch_time_ms


def flatten_dict(d: dict[str, Any], parent_key: str = '', sep: str = '_') -> dict[str, Any]:
    items: list[tuple[str, str]] = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict):
            v_dict: dict[str, Any] = v
            items.extend(flatten_dict(v_dict, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def get_strategy_parameters_max(strategy: object) -> int:
    """
    Get static class values & return the max
    """
    parameters: list[int] = []
    for attr in dir(strategy):
        if attr.startswith('p_'):
            p = getattr(strategy, attr)
            parameters.append(p)
    return max(parameters)


def check_df_has_datetime_index(df: pd.DataFrame) -> bool:
    """
    Checks if the index of a DataFrame is a DatetimeIndex.

    Parameters:
        df (pd.DataFrame): The DataFrame to be checked.

    Returns:
        bool: True if the index is a DatetimeIndex, False otherwise.
    """
    is_datetime_index = isinstance(df.index, pd.DatetimeIndex)
    if not is_datetime_index:
        raise ValueError('Dataframe index is not a DatetimeIndex')
    else:
        return True
    

def coerce_numeric(df: pd.DataFrame) -> pd.DataFrame:
        cols_to_convert = [
                'open', 'close', 'high', 'low', 'volume',
                'number_of_trades', 'quote_asset_volume',
                'taker_buy_asset_volume', 'taker_buy_quote_asset_volume', 
                'average_adr', 'apv'
        ]
        # Filter columns that are both present in the DataFrame and need to be converted.
        filtered_list = [s for s in cols_to_convert if isinstance(s, str) and s in df.columns]
        # Create a new DataFrame with only selected columns converted to numeric type, and return it.
        return pd.concat([df.drop(filtered_list, axis=1), df[filtered_list].apply(pd.to_numeric, errors='coerce')], axis=1)    

