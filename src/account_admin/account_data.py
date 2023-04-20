

from src.helpers.dataclasses import OrderStatusEvent
from src.helpers.util import get_unix_epoch_time_ms
from src.settings import get_settings
from binance.um_futures import UMFutures as Client
from rx.subject import Subject

import asyncio
from binance.websocket.cm_futures.websocket_client import CMFuturesWebsocketClient

from src.util import get_logger


class AccountData:
    """
    Since stop_loss_order or take_profit_order needs to be cancelled if the other is filled, we need a stream of the status
    none is provided via the websocket. This class will be responsible for checking the status of the orders, publishing events 
    on a Subject
    Since rate limits are changed dynamically, the poll interval needs to be adjusted in line with rate limit info from exchangeInfo
    A websocket user stream will be kept open to listen for order updates, this is the primary source of order status, but since disconnects
    could result in missing information polling is required to ensure any missing information is retrieved 

    https://binance-docs.github.io/apidocs/futures/en/#position-information-v2-user_data
    """
   
    def __init__(self, account_data_stream: Subject):
        self.logger = get_logger('AccountData')
        self.kill_polling = False
        self.kill_renew_listen_key = False
        self.account_data_stream = account_data_stream
        self.bi_settings = get_settings('bi')
        self.app_settings = get_settings('app')
        self.client = Client(
            key=self.bi_settings['key'], secret=self.bi_settings['secret'], base_url=self.bi_settings['base_url'])

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
                self.logger.info(f'{count}. get_all_orders: {resp}')
                self.account_data_stream.on_next(OrderStatusEvent(
                    symbol=symbol, payload_type='http', payload=resp))
            if self.kill_polling:
                break
            # pause for 10 seconds before polling again
            await asyncio.sleep(10)

    def get_exchange_info(self):
        """
        Get the exchange info which includes rate limits
        """
        resp = self.client.exchange_info()
        self.logger.info(f'exchange_info: {resp}')
        return resp

    def get_balance(self):
        """
        Get the balance
        """
        resp = self.client.balance(timestamp=get_unix_epoch_time_ms())
        self.logger.info(f'get_balance: {resp}')
        return resp

    async def subscribe_to_user_stream(self):
        """
        Subscribe to the user stream
        """
        def message_handler(message):
            print(message)
            if 'result' not in message or message['result'] is not None:
                
                # Update account_data_stream with OrderStatusEvent, default symbol to 'general' if None
                symbol = message['s'] if message.get('s') is not None else 'general'
                self.account_data_stream.on_next(OrderStatusEvent(
                    symbol=symbol, payload_type='ws', payload=message))

        response = self.client.new_listen_key()
        self.logger.info("Listen key : {}".format(response["listenKey"]))

        user_data_ws_client = CMFuturesWebsocketClient(stream_url=self.bi_settings['stream_url'])
        user_data_ws_client.start()
        self.listen_key=response["listenKey"]
        user_data_ws_client.user_data(
            listen_key=self.listen_key,
            id=1,
            callback=message_handler)
        await self.renew_listen_key()
    
    async def renew_listen_key(self):
        while True:
            await asyncio.sleep(60 * 30)
            response = self.client.renew_listen_key(self.listen_key)
            self.logger.info("renew_listen_key: response : {}".format(response))
            if hasattr(self, 'kill_renew_listen_key') and self.kill_renew_listen_key:
                break
           
