
import pandas as pd
from src.fetch_historical.historical_kline import HistoricalKline
from src.settings import get_settings
from src.stream_consumers.transformers.range_bars import RangeBar
from src.util import clear_logs, clear_symbol_windows, get_logger
from src.window.window import Window
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from rx.subject import Subject
import time

from tests.utils import get_test_out_absolute_path

logging = get_logger('tests')

def new_instance():
    main = Subject()
    settings = get_settings('bi')
    ws_client = UMFuturesWebsocketClient(stream_url=settings['stream_url'])
    window = Window(ws_client, main)
    return window, main

def test_range_bars():
    clear_logs()
    # clear_symbol_windows()
    window, main = new_instance()
    RangeBar(window, main)
    HistoricalKline(main)
    window.start()
    time.sleep(900)
    window.shutdown()

def test_relative_adr_range_size():
    window, main = new_instance()
    rb = RangeBar(window, main)
    csv_path = get_test_out_absolute_path('df_window.csv')
    df_window = pd.read_csv(csv_path)
    df = rb.adv(rb.relative_adr_range_size(df_window))
    assert len(df) > 0