
from src.stream_consumers.transformers.diff_book_bid_ask_sum import DiffBookBidAskSum
from src.stream_consumers.transformers.kline import Kline
from src.window.window import Window
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient

def test_get_consumer_df_name1():
    window = Window(UMFuturesWebsocketClient())
    con = DiffBookBidAskSum(window)
    name = con.df_name
    assert name == 'diff_book_bid_ask_sum'
    
def test_get_consumer_df_name2():
    window = Window(UMFuturesWebsocketClient())
    con = Kline(window)
    name = con.df_name
    assert name == 'kline'

def test_get_consumer_source1():
    window = Window(UMFuturesWebsocketClient())
    con = DiffBookBidAskSum(window)
    name = con.source_name
    assert name == 'diff_book_depth'
   

def test_get_consumer_source2():
    window = Window(UMFuturesWebsocketClient())
    con = Kline(window)
    name = con.source_name
    assert name == 'kline'    
    