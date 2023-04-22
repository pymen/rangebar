
from src.fetch_historical.historical_kline import HistoricalKline
from src.settings import get_settings
from src.stream_consumers.primary_transformers.diff_book_bid_ask_sum import DiffBookBidAskSum
from src.stream_consumers.primary_transformers.kline import Kline
from src.stream_consumers.secondary_transformers.range_bars import RangeBar
from src.util import clear_logs, get_logger
from src.window.window import Window
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from rx.subject import Subject
import time
import asyncio
import pytest

logging = get_logger('tests')

def new_instance():
    main = Subject()
    settings = get_settings('bi')
    ws_client = UMFuturesWebsocketClient(stream_url=settings['stream_url'])
    window = Window(ws_client, main)
    return window, main

def test_get_consumer_df_name1():
    window, main = new_instance()
    con = DiffBookBidAskSum(window, main)
    name = con.df_name
    assert name == 'diff_book_bid_ask_sum'
    
def test_get_consumer_df_name2():
    window, main = new_instance()
    con = Kline(window, main)
    name = con.df_name
    assert name == 'kline'

def test_get_consumer_source1():
    window, main = new_instance()
    con = DiffBookBidAskSum(window, main)
    name = con.source_name
    assert name == 'diff_book_depth'
   

def test_get_consumer_source2():
    window, main = new_instance()
    con = Kline(window, main)
    name = con.source_name
    assert name == 'kline'  

def test_get_consumer_source3():
    window, main = new_instance()
    con = RangeBar(window, main)
    name = con.source_name
    assert name == 'kline'
    
      
    