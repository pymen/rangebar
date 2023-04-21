
from src.fetch_historical.historical_kline import HistoricalKline
from src.settings import get_settings
from src.stream_consumers.transformers.range_bars import RangeBar
from src.util import clear_logs, clear_symbol_windows, get_logger
from src.window.window import Window
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from rx.subject import Subject
import time

logging = get_logger('tests')

def new_instance_with_subjects():
    calc_indicators = Subject()
    historical = Subject()
    settings = get_settings('bi')
    ws_client = UMFuturesWebsocketClient(stream_url=settings['stream_url'])
    window = Window(ws_client, calc_indicators)
    return window, historical, calc_indicators

def test_range_bars():
    clear_logs()
    clear_symbol_windows()
    window, historical, _ = new_instance_with_subjects()
    RangeBar(window, historical)
    HistoricalKline(window, historical)
    window.start()
    time.sleep(240)
    window.shutdown()