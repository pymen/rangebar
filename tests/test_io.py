from src.io.kline_io import KlineIO
from src.io.range_bar_io import RangeBarIO
from src.fetch_historical.historical_kline import HistoricalKline
from src.stream_consumers.exchange.kline import Kline
from src.stream_consumers.rig.range_bars import RangeBar
from src.util import clear_logs, clear_symbol_windows
from rx.subject import Subject # type: ignore
import pandas as pd

from tests.test_utility import test_logging

def test_kline_ingestion() -> None:
    clear_logs()
    clear_symbol_windows()
    primary = Subject()
    KlineIO(primary)
    HistoricalKline(primary)
    kline = Kline(primary)
    RangeBar(primary)
    RangeBarIO(primary)
    kline.start()


def test_df():
    # Create a DatetimeIndex with 10 dates starting from today
    date_rng = pd.date_range(start='2023-04-29', end='2023-05-08', freq='D')

    # Create a DataFrame with random values and use the DatetimeIndex as the index
    df = pd.DataFrame(date_rng, columns=['date'])
    df['data'] = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4]
    df = df.set_index('date')
    df.tz_localize('UTC')
    return df


def test_check_df_contains_processors_window():
    df = test_df()
    """Check if df contains the processors window"""
    processors_window = pd.Timedelta('30min')
    missing_date_range = pd.Timestamp.utcnow() - df.index.max()
    result = missing_date_range > processors_window
    print(f'check_df_contains_processors_window: missing_date_range: {missing_date_range}, processors_window: {processors_window}, result: {result}')
   


