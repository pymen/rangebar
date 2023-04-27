from src.fetch_historical.historical_kline import HistoricalKline
from src.helpers.dataclasses import HistoricalKlineEvent
from src.stream_consumers.primary_transformers.kline import Kline
from src.util import get_logger
from src.data_frame_io.abstract_data_frame_io import AbstractDataFrameIO
from rx.subject import Subject
import pandas as pd
import datetime

logging = get_logger('tests')

def new_instance():
    primary = Subject()
    secondary = Subject()
    AbstractDataFrameIO('kline', primary, secondary)
    kline = Kline(primary, secondary)
    return HistoricalKline(primary), kline

def test_get_1000_minute_intervals():
    target, _ = new_instance()
    last_timestamp = pd.to_datetime('2023-04-07 00:00:00') 
    pairs = target.get_1000_minute_intervals(last_timestamp)
    assert len(pairs) == 11

def test_fetch_all_intervals():
    target, _ = new_instance()
    last_timestamp = pd.to_datetime('2023-04-07 00:00:00') 
    pairs = target.get_1000_minute_intervals(last_timestamp)
    e = HistoricalKlineEvent(symbol='btcusdt', source='kline', last_timestamp=last_timestamp) 
    resp_data = target.fetch_all_intervals(e, pairs)
    logging.debug(f'resp_data.len: {len(resp_data)}')

def chunk_array(arr, chunk_size=10000):
    return [arr[i:i+chunk_size] for i in range(0, len(arr), chunk_size)]


def test_build_df():
    target, _ = new_instance()
    last_timestamp = pd.to_datetime('2023-04-20 00:00:00') 
    pairs = target.get_1000_minute_intervals(last_timestamp)
    e = HistoricalKlineEvent(symbol='btcusdt', source='kline', last_timestamp=last_timestamp) 
    resp_data = target.fetch_all_intervals(e, pairs)
    logging.debug(f'resp_data.len: {str(resp_data)}')
    # df = target.build_df(resp_data)
    # logging.debug(f'df len: {len(df)}')

def test_fetch_historical():
    target, _ = new_instance()
    last_timestamp = pd.to_datetime('2023-04-07 00:00:00') 
    e = HistoricalKlineEvent(symbol='btcusdt', source='kline', last_timestamp=last_timestamp)    


def test_timedelta():
    to_time_now = datetime.datetime.now() 
    last_timestamp = pd.to_datetime('2023-03-24 08:56:00')
    minutes = int((to_time_now - last_timestamp).total_seconds() / 60) 
    logging.debug(f'minutes: {minutes}')    
    # Get the number of 1000 minute intervals
    intervals = int(minutes / 1000)
    logging.debug(f'intervals: {intervals}')
    # Get the remainder
    remainder = minutes % 1000
    if remainder > 0:
        intervals = intervals + (1 if intervals % 2 == 1 else 2)
        logging.debug(f'new intervals: {intervals}')
    # Create a list of pairs of start and end times
    stamps = [to_time_now]
    for i in range(1, intervals):
        bound = to_time_now - datetime.timedelta(minutes=1000*i)
        stamps.append(bound)
    
    logging.debug(f'stamps.len: {len(stamps)}')
    stamps = stamps[::-1]
    pairs = [[stamps[i], stamps[i+1]] for i in range(0, len(stamps) - 1)]
    logging.debug(f'pairs.len: {len(pairs)}')
    for pair in pairs:
        logging.debug(f'{pair[0]} - {pair[1]}')
    output = []
    for i in range(len(pairs) - 1):
        start, end = pairs[i]
        diff_minutes = int((end - start).total_seconds() / 60)
        output.append(f"Minutes between {str(start)} and {str(end)}: {diff_minutes}")
    # Calculate the difference between the last pair of timestamps
    last_start, last_end = pairs[-1]
    last_diff_minutes = int((last_end - last_start).total_seconds() / 60)
    output.append(f"Minutes between {str(last_start)} and {str(last_end)}: {last_diff_minutes}")
    
    logging.debug(f'number of output messages: {len(output)}')
    logging.debug("\n".join(output))    
