from src.fetch_historical.historical_kline import HistoricalKline
from src.helpers.dataclasses import FetchHistoricalEvent
from src.window.window import Window
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from rx.subject import Subject
import pandas as pd

def test_fetch_historical():
    historical = Subject()
    window = Window(UMFuturesWebsocketClient(), Subject(), historical)
    target = HistoricalKline(window)
    last_timestamp = pd.to_datetime('2023-04-04 00:00:00') 
    e = FetchHistoricalEvent(symbol='btcusdt', source='kline', last_timestamp=last_timestamp)
    # historical.next(e)
    df = target.fetch_historical(e)
    df.to_clipboard()