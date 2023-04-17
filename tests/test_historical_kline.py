from src.fetch_historical.historical_kline import HistoricalKline
from src.helpers.dataclasses import FetchHistoricalEvent
from src.settings import get_settings
from src.window.window import Window
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from rx.subject import Subject
import pandas as pd
import datetime
from src.main import stream_url

def new_instance():
    historical = Subject()
    settings = get_settings('bi')
    window = Window(UMFuturesWebsocketClient(stream_url=settings['stream_url']), Subject(), historical)
    return HistoricalKline(window)

def test_get_1000_minute_intervals():
    target = new_instance()
    last_timestamp = pd.to_datetime('2023-04-07 00:00:00') 
    pairs = target.get_1000_minute_intervals(last_timestamp)
    assert len(pairs) == 11

def test_fetch_all_intervals():
    target = new_instance()
    last_timestamp = pd.to_datetime('2023-04-07 00:00:00') 
    pairs = target.get_1000_minute_intervals(last_timestamp)
    e = FetchHistoricalEvent(symbol='btcusdt', source='kline', last_timestamp=last_timestamp) 
    resp_data = target.fetch_all_intervals(e, pairs)
    print(f'resp_data.len: {len(resp_data)}')

def chunk_array(arr, chunk_size=10000):
    return [arr[i:i+chunk_size] for i in range(0, len(arr), chunk_size)]


def test_build_df():
    target = new_instance()
    last_timestamp = pd.to_datetime('2022-04-14 00:00:00') 
    pairs = target.get_1000_minute_intervals(last_timestamp)
    e = FetchHistoricalEvent(symbol='btcusdt', source='kline', last_timestamp=last_timestamp) 
    resp_data = target.fetch_all_intervals(e, pairs)
    print(f'resp_data.len: {len(resp_data)}')
    df = target.build_df(resp_data)
    print(f'df len: {len(df)}')

def test_fetch_historical():
    target = new_instance()
    last_timestamp = pd.to_datetime('2023-04-07 00:00:00') 
    e = FetchHistoricalEvent(symbol='btcusdt', source='kline', last_timestamp=last_timestamp)    


def test_timedelta():
    to_time_now = datetime.datetime.now() 
    last_timestamp = pd.to_datetime('2023-03-24 08:56:00')
    minutes = int((to_time_now - last_timestamp).total_seconds() / 60) 
    print(f'minutes: {minutes}')    
    # Get the number of 1000 minute intervals
    intervals = int(minutes / 1000)
    print(f'intervals: {intervals}')
    # Get the remainder
    remainder = minutes % 1000
    if remainder > 0:
        intervals = intervals + (1 if intervals % 2 == 1 else 2)
        print(f'new intervals: {intervals}')
    # Create a list of pairs of start and end times
    stamps = [to_time_now]
    for i in range(1, intervals):
        bound = to_time_now - datetime.timedelta(minutes=1000*i)
        stamps.append(bound)
    
    print(f'stamps.len: {len(stamps)}')
    stamps = stamps[::-1]
    pairs = [[stamps[i], stamps[i+1]] for i in range(0, len(stamps) - 1)]
    print(f'pairs.len: {len(pairs)}')
    for pair in pairs:
        print(f'{pair[0]} - {pair[1]}')
    output = []
    for i in range(len(pairs) - 1):
        start, end = pairs[i]
        diff_minutes = int((end - start).total_seconds() / 60)
        output.append(f"Minutes between {str(start)} and {str(end)}: {diff_minutes}")
    # Calculate the difference between the last pair of timestamps
    last_start, last_end = pairs[-1]
    last_diff_minutes = int((last_end - last_start).total_seconds() / 60)
    output.append(f"Minutes between {str(last_start)} and {str(last_end)}: {last_diff_minutes}")
    
    print(f'number of output messages: {len(output)}')
    print("\n".join(output))    
