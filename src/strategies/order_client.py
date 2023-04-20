from datetime import datetime
from binance.um_futures import UMFutures as Client
from binance.error import ClientError
from src.settings import get_settings
import logging
from src.util import get_logger


class OrderClient:
    """
    These are not OCO orders in the case of a stop_loss_order being activated, the take_profit_order needs to be cancelled.
    Conversely, if the take_profit_order is activated, the stop_loss_order needs to be cancelled
    The common suffix for the orders is the unix epoch time in milliseconds & meant to provide a link between the orders
    so that the appropriate order can be cancelled when the other is activated

    Not a limit order is not guaranteed to be filled! If it isn't the other 2 in the group should also be canceled
    """
    trades = []

    def __init__(self):
        self.logger = get_logger('OrderClient')
        self.settings = get_settings('bi')
        self.client = Client(
            api_key=self.settings['key'], secret_key=self.settings['secret'])

   
    def buy(self, symbol: str, quantity: int, stop_loss: str, take_profit: str, entry_price: str):
        """
        BTC 0.001 is called a millibitcoin or mBTC. It is one-thousandth of a bitcoin (BTC)
        min quantity is 0.001

        This would be equivalent, with BTC to a so called pip in forex trading
        but likely different for other coins
        """
        sl_tp_order_id_prefix = self.get_unix_epoch_time_ms(datetime.now())
        sl_id = f'{sl_tp_order_id_prefix}_b_sl'
        tp_id = f'{sl_tp_order_id_prefix}_b_tp'
        bo_id = f'{sl_tp_order_id_prefix}_b_bo'
        params = [
            {
                "strategySubId": 1,
                "firstDrivenId": 0,
                "secondDrivenId": 0,
                "securityType": "USDT_FUTURES",
                "reduceOnly": False,

                "side": "BUY",
                "positionSide": "BOTH",
                "symbol": symbol,
                "quantity": quantity,
                "price": entry_price,
                "timeInForce": "GTC",
                "newClientOrderId": bo_id,
                "type": "LIMIT"
                
            },
            {
                "securityType": "USDT_FUTURES",
                "firstTrigger": "PLACE_ORDER",
                "firstDrivenOn": "PARTIALLY_FILLED_OR_FILLED",
                "reduceOnly": True,
                "strategySubId": 2,
                "firstDrivenId": 1,
                "secondDrivenId": 3,
                "secondDrivenOn": "PARTIALLY_FILLED_OR_FILLED",
                "secondTrigger": "CANCEL_ORDER",
                "workingType": "MARK_PRICE",
                "priceProtect": True,

                "side": "SELL",
                "positionSide": "BOTH",
                "symbol": symbol,
                "quantity": quantity,
                "stopPrice": take_profit,
                "timeInForce": "GTE_GTC",
                "newClientOrderId": tp_id,
                "type": "TAKE_PROFIT_MARKET"
                
            },
            {
                "securityType": "USDT_FUTURES",
                "firstTrigger": "PLACE_ORDER",
                "firstDrivenOn": "PARTIALLY_FILLED_OR_FILLED",
                "reduceOnly": True,
                "strategySubId": 3,
                "firstDrivenId": 1,
                "secondDrivenId": 2,
                "secondDrivenOn": "PARTIALLY_FILLED_OR_FILLED",
                "secondTrigger": "CANCEL_ORDER",
                "workingType": "MARK_PRICE",
                "priceProtect": True,

                "side": "SELL",
                "positionSide": "BOTH",
                "symbol": symbol,
                "quantity": quantity,
                "stopPrice": stop_loss,
                "timeInForce": "GTE_GTC",
                "newClientOrderId": sl_id,
                "type": "STOP_MARKET"
                
            }
        ]
        try:
            response = self.client.new_batch_order(params)
            self.trades.append((sl_id, tp_id, bo_id))
            self.logger.info(response)
        except ClientError as error:
            self.logger.error(
                "Found error. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message
                )
            )

    def sell(self, symbol: str, quantity: int, stop_loss: str, take_profit: str, entry_price: str):
        """
        BTC 0.001 is called a millibitcoin or mBTC. It is one-thousandth of a bitcoin (BTC)
        min quantity is 0.001

        This would be equivalent, with BTC to a so called pip in forex trading
        but likely different for other coins
        """
        sl_tp_order_id_prefix = self.get_unix_epoch_time_ms(datetime.now())
        sl_id = f'{sl_tp_order_id_prefix}_s_sl'
        tp_id = f'{sl_tp_order_id_prefix}_s_tp'
        bo_id = f'{sl_tp_order_id_prefix}_s_bo'
        params = [
            {
                "strategySubId": 1,
                "firstDrivenId": 0,
                "secondDrivenId": 0,
                "securityType": "USDT_FUTURES",
                "reduceOnly": False,

                "side": "SELL",
                "positionSide": "BOTH",
                "symbol": symbol,
                "quantity": quantity,
                "price": entry_price,
                "timeInForce": "GTC",
                "newClientOrderId": bo_id,
                "type": "LIMIT"
            },
            {
                "strategySubId": 2,
                "firstDrivenId": 1,
                "secondDrivenId": 3,
                "secondDrivenOn": "PARTIALLY_FILLED_OR_FILLED",
                "secondTrigger": "CANCEL_ORDER",
                "securityType": "USDT_FUTURES",
                "firstTrigger": "PLACE_ORDER",
                "firstDrivenOn": "PARTIALLY_FILLED_OR_FILLED",
                "workingType": "MARK_PRICE",
                "priceProtect": True,
                "reduceOnly": True,

                "side": "BUY",
                "positionSide": "BOTH",
                "symbol": symbol,
                "quantity": quantity,
                "stopPrice": take_profit,
                "timeInForce": "GTE_GTC",
                "newClientOrderId": tp_id,
                "type": "TAKE_PROFIT_MARKET",
            },
            {
                "strategySubId": 3,
                "firstDrivenId": 1,
                "secondDrivenId": 2,
                "secondDrivenOn": "PARTIALLY_FILLED_OR_FILLED",
                "secondTrigger": "CANCEL_ORDER",
                "workingType": "MARK_PRICE",
                "priceProtect": True,
                "securityType": "USDT_FUTURES",
                "firstTrigger": "PLACE_ORDER",
                "firstDrivenOn": "PARTIALLY_FILLED_OR_FILLED",
                "reduceOnly": True,

                "side": "BUY",
                "positionSide": "BOTH",
                "symbol": symbol,
                "quantity": quantity,
                "stopPrice": stop_loss,
                "timeInForce": "GTE_GTC",
                "newClientOrderId": sl_id,
                "type": "STOP_MARKET"
            }
        ]
        try:
            response = self.client.new_batch_order(params)
            self.trades.append((sl_id, tp_id, bo_id))
            self.logger.info(response)
        except ClientError as error:
            self.logger.error(
                "Found error. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message
                )
            )

    def cancel_order(self, symbol, order_id):
        try:
            response = self.client.cancel_order(
                symbol=symbol, orderId=order_id, recvWindow=5000
            )
            self.logger.info(f'Order cancelled: {response}')
        except ClientError as error:
            self.logger.info(
                "Found error. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message
                )
            )

    
