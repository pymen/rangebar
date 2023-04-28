from typing import Any
from rx import operators as ops
from rx.core.pipe import pipe
from src.helpers.dataclasses import CmdEvent, DataEvent # type: ignore
import pandas as pd

def sanitize_numeric_columns_df():
    def to_numeric(df: pd.DataFrame) -> pd.DataFrame:
        cols_to_convert = [
                'open', 'close', 'high', 'low', 'volume',
                'number_of_trades', 'quote_asset_volume',
                'taker_buy_asset_volume', 'taker_buy_quote_asset_volume', 
                'average_adr', 'apv'
        ]
        filtered_list = [s for s in cols_to_convert if isinstance(s, str) and s in df.columns]
        df[filtered_list] = df[filtered_list].apply(lambda x: pd.to_numeric(x, errors='coerce'))
        return df
    
    def sanitize(e: Any) -> Any:
        if isinstance(e, DataEvent):
            e.df = to_numeric(e.df)
        elif isinstance(e, CmdEvent):
            for k, v in e.kwargs.items():
                if isinstance(v, pd.DataFrame):
                    e.kwargs[k] = to_numeric(v)
        return e
    return pipe.compose(
        ops.map(sanitize),
    )