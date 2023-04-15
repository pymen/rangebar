

from src.helpers.dataclasses import OrderStatusEvent
from src.helpers.util import get_unix_epoch_time_ms
from src.settings import get_settings
from binance.um_futures import UMFutures as Client
from rx.subject import Subject
from src.window.window import Window
import logging
from src.main import base_url
import asyncio
from datetime import datetime

class AccountStatus:
    """
    Since stop_loss_order or take_profit_order needs to be cancelled if the other is filled, we need a stream of the status
    none is provided via the websocket. This class will be responsible for checking the status of the orders, publishing events 
    on a Subject
    Since rate limits are changed dynamically, the poll interval needs to be adjusted in line with rate limit info from exchangeInfo
    A websocket user stream will be kept open to listen for order updates, this is the primary source of order status, but since disconnects
    could result in missing information polling is required to ensure any missing information is retrieved 
    """
    kill_polling = False
    def __init__(self, window: Window, order_status: Subject):
        self.window = window
        self.order_status = order_status
        self.bi_settings = get_settings('bi')
        self.app_settings = get_settings('app')
        self.client = Client(key=self.bi_settings['key'], secret=self.bi_settings['secret'], base_url=base_url)

 

    async def poll(self):
        """
        Poll the order status asynchronously.
        Test response for get_exchange_info was:
        {
            "rateLimitType": "ORDERS",
            "interval": "MINUTE",
            "intervalNum": 1,
            "limit": 1200
        }
        Much more than we need, so every 10 seconds should be fine.
        """
        count = 0
        while True:
            for symbols_config in self.app_settings['symbols_config']:
                symbol = symbols_config['symbol']
                resp = await self.client.get_all_orders(symbol=symbol, timestamp=get_unix_epoch_time_ms())
                count += 1
                logging.info(f'{count}. get_all_orders: {resp}')
                self.order_status.on_next(OrderStatusEvent(symbol=symbol, payload_type='http', payload=resp))
            if self.kill_polling:
                break    
            # pause for 10 seconds before polling again
            await asyncio.sleep(10)
        

    def get_exchange_info(self):
        """
        Get the exchange info which includes rate limits
        """
        resp = self.client.exchange_info()
        logging.info(f'exchange_info: {resp}')
        return resp
    
    def get_balance(self):
        """
        Get the balance
        """
        resp = self.client.balance(timestamp=get_unix_epoch_time_ms())
        logging.info(f'get_balance: {resp}')
        return resp