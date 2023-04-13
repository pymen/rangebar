
from src.stream_consumers.transformers.diff_book_bid_ask_sum import DiffBookBidAskSum
from src.stream_consumers.transformers.kline import Kline
from src.window.window import Window
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from rx.subject import Subject


def generate_window():
    calc_indicators = Subject()
    historical = Subject()
    ws_client = UMFuturesWebsocketClient()
    window = Window(ws_client, calc_indicators, historical)
    return window

def test_get_consumer_df_name1():
    window = generate_window()
    con = DiffBookBidAskSum(window)
    name = con.df_name
    assert name == 'diff_book_bid_ask_sum'
    
def test_get_consumer_df_name2():
    window = generate_window()
    con = Kline(window)
    name = con.df_name
    assert name == 'kline'

def test_get_consumer_source1():
    window = generate_window()
    con = DiffBookBidAskSum(window)
    name = con.source_name
    assert name == 'diff_book_depth'
   

def test_get_consumer_source2():
    window = generate_window()
    con = Kline(window)
    name = con.source_name
    assert name == 'kline'    
    