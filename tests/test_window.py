

from src.settings import get_settings
from src.stream_consumers.transformers.diff_book_bid_ask_sum import DiffBookBidAskSum
from src.stream_consumers.transformers.kline import Kline
from src.window.window import Window
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from rx.subject import Subject

def new_instance():
    settings = get_settings('bi')
    ws_client = UMFuturesWebsocketClient(stream_url=settings['stream_url'])
    window = Window(ws_client, Subject(), Subject())
    return window

def test_window_start_init():
    window = new_instance()
    assert window is not None
    print("window.symbol_dict_df_dict: ", window.symbol_dict_df_dict)

def test_window_start():
    window = new_instance()
    window.start()

def test_get_symbol_grouped_csv_paths():
    window = new_instance()
    window.get_df_names_from_csv_paths()

def test_get_consumer_triggers():
    window = new_instance()
    DiffBookBidAskSum(window)
    Kline(window)
    symbol = get_settings('app')['symbols'][0]
    consumer_dict = window.consumers[symbol]
    triggers = []
    for _, consumer in consumer_dict.items():
        triggers = window.get_consumer_triggers(consumer)
        break
    assert len(triggers) > 0

def test_eval_count_triggers():
    window = new_instance()
    DiffBookBidAskSum(window)
    Kline(window)
    window.eval_count_triggers()  
    

    