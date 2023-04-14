

from src.settings import get_settings
from binance.um_futures import UMFutures as Client
from rx.subject import Subject
from src.window.window import Window


class OrderStatus:
    """
    Since stop_loss_order or take_profit_order needs to be cancelled if the other is filled, we need a stream of the status
    none is provided via the websocket. This class will be responsible for checking the status of the orders, publishing events 
    on a Subject
    """

    def __init__(self, window: Window, order_status: Subject):
        self.window = window
        self.order_status = order_status
        self.settings = get_settings('bi')
        self.client = Client(api_key=self.settings['g_api_key'], secret_key=self.settings['g_secret_key'])

    def poll(self):
        """
        Poll the order status
        """
        for symbols_config in self.settings['symbols_config']:
            self.client.get_all_orders(symbol=symbols_config['symbol'])
        pass