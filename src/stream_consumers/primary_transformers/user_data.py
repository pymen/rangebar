

from typing import Any
from src.helpers.dataclasses import OrderStatusEvent
from src.helpers.util import flatten_dict, get_unix_epoch_time_ms
from src.settings import get_settings
from binance.um_futures import UMFutures as Client
from rx.subject import Subject # type: ignore
import asyncio
from binance.websocket.cm_futures.websocket_client import CMFuturesWebsocketClient
from src.util import get_logger


class UserData:
    """
    Since stop_loss_order or take_profit_order needs to be cancelled if the other is filled, we need a stream of the status
    none is provided via the websocket. This class will be responsible for checking the status of the orders, publishing events 
    on a Subject
    Since rate limits are changed dynamically, the poll interval needs to be adjusted in line with rate limit info from exchangeInfo
    A websocket user stream will be kept open to listen for order updates, this is the primary source of order status, but since disconnects
    could result in missing information polling is required to ensure any missing information is retrieved 

    https://binance-docs.github.io/apidocs/futures/en/#position-information-v2-user_data
    """
   
    def __init__(self, primary: Subject):
        self.logger = get_logger('AccountData')
        self.kill_polling = False
        self.kill_renew_listen_key = False
        self.listen_key = ''
        self.primary = primary
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
                resp = await self.client.get_all_orders(symbol=symbol, timestamp=get_unix_epoch_time_ms()) # type: ignore
                count += 1
                self.logger.info(f'{count}. get_all_orders: {resp}')
                self.primary.on_next(OrderStatusEvent(
                    symbol=symbol, payload_type='http', payload=resp)) # type: ignore
            if self.kill_polling:
                break
            # pause for 10 seconds before polling again
            await asyncio.sleep(10)

    def get_exchange_info(self) -> dict[str, Any]:
        """
        Get the exchange info which includes rate limits
        """
        resp = self.client.exchange_info() # type: ignore
        self.logger.info(f'exchange_info: {resp}')
        return resp # type: ignore

    def get_balance(self) -> dict[str, Any]:
        """
        Get the balance
        """
        resp = self.client.balance(timestamp=get_unix_epoch_time_ms()) # type: ignore
        self.logger.info(f'get_balance: {resp}')
        return resp # type: ignore

    async def subscribe_to_user_stream(self):
        """
        Subscribe to the user stream
        """
        def message_handler(message: dict[str, Any]):
            print(message)
            if 'result' not in message or message['result'] is not None:
                
                # Update main with OrderStatusEvent, default symbol to 'general' if None
                symbol: str = message['s'] if message.get('s') is not None else 'general'
                self.primary.on_next(OrderStatusEvent(
                    symbol=symbol, payload_type='ws', payload=message))

        response: dict[str, str] = self.client.new_listen_key() # type: ignore
        my_listen_key: str = response["listenKey"] # type: ignore
        self.logger.info(f"Listen key : {my_listen_key}")

        user_data_ws_client = CMFuturesWebsocketClient(stream_url=self.bi_settings['stream_url'])
        user_data_ws_client.start()
        self.listen_key: str = my_listen_key
        user_data_ws_client.user_data( # type: ignore
            listen_key=self.listen_key,  # type: ignore
            id=1,
            callback=message_handler) # type: ignore
        await self.renew_listen_key()
    
    async def renew_listen_key(self):
        while True:
            await asyncio.sleep(60 * 30)
            response: dict[str, str] = self.client.renew_listen_key(self.listen_key) # type: ignore
            self.logger.info(f"renew_listen_key: response : {response}")
            if hasattr(self, 'kill_renew_listen_key') and self.kill_renew_listen_key:
                break

    def map_raw_payload(self, e: dict[str, Any]):
        event_type = e['e']
        if event_type == 'ACCOUNT_CONFIG_UPDATE':
            mapping = {
                "e": "event_type",
                "E": "event_time",
                "T": "transaction_time",
                "ac_s": "symbol",
                "ac_l": "leverage",
                "ai_j": "multi_assets_mode"
            }
            # there are no lists so flattening first makes sense for this one
            flat = flatten_dict(e)
            result = self.map_payload(mapping, flat)
            return result
        elif event_type == 'ACCOUNT_UPDATE':
            mapping = {
                "e": "event_type",
                "E": "event_time",
                "T": "transaction",
                "a_m": "event_reason_type",
                "a_B": "balances",
                "a_P": "positions"
            }
            positions_array_item = {
                "s": "symbol",
                "pa": "position_amount",
                "ep": "entry_price",
                "cr": "pre_fee_accumulated_realized",
                "up": "unrealized_pn_l",
                "mt": "margin_type",
                "iw": "isolated_wallet",
                "ps": "position_side"
            }
            balances_array_item = {
                "a": "asset",
                "wb": "wallet_balance",
                "cw": "cross_wallet_balance",
                "bc": "balance_change_except_pnl_and_commission"
            }
            # there are no lists so flattening first makes sense for this one
            flat = flatten_dict(e)
            result = self.map_payload(mapping, flat)
            positions: list[dict[str, str]] = []
            for p in result['positions']:
                positions.append(self.map_payload(positions_array_item, p))
            result['positions'] = positions
            balances: list[dict[str, str]] = []
            for b in result['balances']:
                balances.append(self.map_payload(balances_array_item, b))
            result['balances'] = balances
            return result     
        elif event_type == 'MARGIN_CALL':
            mapping = {
                "e": "event_type",
                "E": "event_time",
                "cw": "cross_wallet_balance",
                "p": "positions"
            }
            positions_array_item = {
                "s": "symbol",
                "ps": "position_side",
                "pa": "position_amount",
                "mt": "margin_type",
                "iw": "isolated_wallet",
                "mp": "mark_price",
                "up": "unrealized_pnl",
                "mm": "maintenance_margin_required"
            }
            result = self.map_payload(mapping, e)
            positions: list[dict[str, str]] = []
            for p in result['positions']:
                positions.append(self.map_payload(positions_array_item, p))
            result['positions'] = positions
            return result    
        elif event_type == 'ORDER_TRADE_UPDATE':
            mapping = {
                "e": "event_type",
                "E": "event_time",
                "T": "transaction_time",
                "o_s": "symbol",
                "o_c": "client_order_id",
                "o_S": "side",
                "o_f": "timein_force",
                "o_q": "original_quantity",
                "o_p": "original_price",
                "o_ap": "average_price",
                "o_sp": "stop_price",
                "o_x": "execution_type",
                "o_X": "order_status",
                "o_i": "order_id",
                "o_l": "order_last_filled_quantity",
                "o_z": "order_filled_accumulated_quantity",
                "o_L": "last_filled_price",
                "o_N": "commission_asset",
                "o_n": "commission",
                "o_T": "transaction_time",
                "o_t": "trade_id",
                "o_b": "bids_notional",
                "o_a": "average_price",
                "o_m": "trade_maker_side",
                "o_R": "reduce_only",
                "o_wt": "stop_price_working_type",
                "o_ot": "original_order_type",
                "o_ps": "position_side",
                "o_cp": "close_all",
                "o_AP": "activation_price",
                "o_cr": "callback_rate",
                "o_rp": "realized_profit"
            }
            # there are no lists so flattening first makes sense for this one
            flat = flatten_dict(e)
            result = self.map_payload(mapping, flat)


    def map_payload(self, mapping: dict[str, str], input_dict: dict[str, Any]) -> dict[str, Any]:
        output_dict: dict[str, str] = {}
        for key, value in input_dict.items():
            if key in mapping:
                output_dict[mapping[key]] = value
        return output_dict        
        
           
