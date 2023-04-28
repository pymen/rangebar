import pandas as pd
import numpy as np
from tests.utils import get_test_out_absolute_path
from tests.utils import test_logger

def setup():
    csv_path = get_test_out_absolute_path('sample-with-date.csv')
    df = pd.read_csv(csv_path, parse_dates=['timestamp'], index_col='timestamp')
    return df

def test_add_adr_logic():
    df = setup()
    try:
        daily_high_low = df.groupby(  # type: ignore
            'date')[['high', 'low']].agg(['max', 'min']) # type: ignore
        logger.debug(f"adr: daily_high_low: {str(daily_high_low)}")  # type: ignore
        high_max: pd.Series = daily_high_low[('high', 'max')]
        low_min: pd.Series = daily_high_low[('low', 'min')]
        # convert the Series to numeric values
        high_max = pd.to_numeric(high_max, errors='coerce')
        low_min = pd.to_numeric(low_min, errors='coerce')
        logger.debug(f"adr: high_max: {high_max.to_list()} ({type(high_max)}),  low_min: {low_min.to_list()} ({type(low_min)})")  # type: ignore
        adr = high_max - low_min # type: ignore
        test_logger.debug(f"adr: vector subtraction: dr: {adr}")
        daily_high_low['adr'] = adr
        average_adr = np.mean(daily_high_low['adr'])  # type: ignore
        logger.info(f"result: adr: average_adr: {str(average_adr)}")  # type: ignore
    except Exception as e:
        test_logger.error(f"adr: {str(e)}")
        