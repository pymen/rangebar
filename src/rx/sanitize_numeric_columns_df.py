from typing import Any
from rx import operators as ops
from rx.core.pipe import pipe
from src.helpers.dataclasses import CmdEvent, DataEvent # type: ignore
import pandas as pd
from src.helpers.util import coerce_numeric

# FIXME in a pipe it gives an error module is not callable
# def sanitize_numeric_columns_df() -> Callable[[Observable], Observable]:
# https://rxpy.readthedocs.io/en/latest/get_started.html#custom-operator
def sanitize_numeric_columns_df():
    def sanitize(e: Any) -> Any:
        if isinstance(e, DataEvent):
            e.df = coerce_numeric(e.df)
        elif isinstance(e, CmdEvent):
            for k, v in e.kwargs.items():
                if isinstance(v, pd.DataFrame):
                    e.kwargs[k] = coerce_numeric(v)
        return e
    
    return pipe(
        ops.map(sanitize),
    )