

from src.settings import get_settings
from binance.um_futures import UMFutures as Client
from rx.subject import Subject
from src.window.window import Window
import logging
from src.main import base_url

class OrderStatus:
    """
    Since stop_loss_order or take_profit_order needs to be cancelled if the other is filled, we need a stream of the status
    none is provided via the websocket. This class will be responsible for checking the status of the orders, publishing events 
    on a Subject
    Since rate limits are changed dynamically, the poll interval needs to be adjusted in line with rate limit info from exchangeInfo
    A websocket user stream will be kept open to listen for order updates, this is the primary source of order status, but since disconnects
    could result in missing information polling is required to ensure any missing information is retrieved 
    """

    def __init__(self, window: Window, order_status: Subject):
        self.window = window
        self.order_status = order_status
        self.settings = get_settings('bi')
        self.client = Client(key=self.settings['g_api_key'], secret=self.settings['g_secret_key'], base_url=base_url)

    def poll(self):
        """
        Poll the order status
        """
        for symbols_config in self.settings['symbols_config']:
            self.client.get_all_orders(symbol=symbols_config['symbol'])
        pass

    def get_exchange_info(self):
        """
        Get the exchange info which includes rate limits
        """
        resp = self.client.exchange_info()
        logging.info(f'exchange_info: {resp}')
        return resp