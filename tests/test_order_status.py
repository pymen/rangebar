from src.strategies.order_status import OrderStatus
from src.window.window import Window
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from rx.subject import Subject
from src.main import stream_url

def new_instance():
    order_status = Subject()
    window = Window(UMFuturesWebsocketClient(stream_url=stream_url), Subject(), Subject())
    os = OrderStatus(window, order_status)
    return os


def test_get_exchange_info():
    target = new_instance()
    resp = target.get_exchange_info()
    print(f'resp: {resp}')