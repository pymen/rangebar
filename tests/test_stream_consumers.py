
from src.settings import get_settings
from src.stream_consumers.transformers.diff_book_bid_ask_sum import DiffBookBidAskSum
from src.stream_consumers.transformers.kline import Kline
from src.window.window import Window
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from rx.subject import Subject

def new_instance():
    calc_indicators = Subject()
    historical = Subject()
    settings = get_settings('bi')
    ws_client = UMFuturesWebsocketClient(stream_url=settings['stream_url'])
    window = Window(ws_client, calc_indicators, historical)
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
    