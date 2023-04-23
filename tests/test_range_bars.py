
import numpy as np
import pandas as pd
from src.fetch_historical.historical_kline import HistoricalKline
from src.stream_consumers.primary_transformers.kline import Kline
from src.stream_consumers.secondary_transformers.range_bars import RangeBar
from src.util import clear_logs, get_logger
from src.data_frame_io.data_frame_io import DataFrameIO
from rx.subject import Subject
import rx.operators as op
import time
import asyncio
import pytest
from tests.utils import get_test_out_absolute_path

"""
The goal is to have a df in memory & saved to csv for range bars.
"""

logger = get_logger('test_range_bars')

def test_kline_df():
    primary = Subject()
    secondary = Subject()
    kline_df = DataFrameIO('kline', primary, secondary)
    HistoricalKline(primary)
    kline = Kline(primary)
    kline.start()
    time.sleep(120)
    kline_df.save_symbol_df_data()
    kline.stop()

def test_range_bars():
    primary = Subject()
    secondary = Subject()
    kline_df = DataFrameIO('kline', primary, secondary)
    HistoricalKline(primary)
    range_bar_df = DataFrameIO('range_bar', primary, secondary)
    kline = Kline(primary, secondary)
    range_bar = RangeBar(primary, secondary)





