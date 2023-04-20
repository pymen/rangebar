
from src.fetch_historical.historical_kline import HistoricalKline
from src.settings import get_settings
from src.stream_consumers.transformers.diff_book_bid_ask_sum import DiffBookBidAskSum
from src.stream_consumers.transformers.kline import Kline
from src.stream_consumers.transformers.range_bars import RangeBar
from src.util import get_logger
from src.window.window import Window
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from rx.subject import Subject
import time
from tests.utils import init_logging
import asyncio
import pytest

logging = get_logger('tests')

def new_instance_with_subjects():
    calc_indicators = Subject()
    historical = Subject()
    settings = get_settings('bi')
    ws_client = UMFuturesWebsocketClient(stream_url=settings['stream_url'])
    window = Window(ws_client, calc_indicators)
    return window, historical, calc_indicators

def new_instance():
    window, _, _ = new_instance_with_subjects()
    return window

def test_get_consumer_df_name1():
    window = new_instance()
    con = DiffBookBidAskSum(window)
    name = con.df_name
    assert name == 'diff_book_bid_ask_sum'
    
def test_get_consumer_df_name2():
    window = new_instance()
    con = Kline(window)
    name = con.df_name
    assert name == 'kline'

def test_get_consumer_source1():
    window = new_instance()
    con = DiffBookBidAskSum(window)
    name = con.source_name
    assert name == 'diff_book_depth'
   

def test_get_consumer_source2():
    window = new_instance()
    con = Kline(window)
    name = con.source_name
    assert name == 'kline'  

def test_get_consumer_source3():
    window = new_instance()
    con = RangeBar(window)
    name = con.source_name
    assert name == 'kline'      


def test_range_bars():
    window, historical, _ = new_instance_with_subjects()
    RangeBar(window, historical)
    HistoricalKline(window, historical)
    window.start()
    time.sleep(240)
    window.shutdown()
    
      
    