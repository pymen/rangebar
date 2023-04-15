from datetime import datetime
from binance.um_futures import UMFutures as Client
from binance.error import ClientError
from src.settings import get_settings
import logging

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
        self.settings = get_settings('bi')
        self.client = Client(api_key=self.settings['g_api_key'], secret_key=self.settings['g_secret_key'])
    
       
    def buy(self, symbol, quantity, stop_loss, take_profit, entry_price):
        sl_tp_order_id_prefix = self.get_unix_epoch_time_ms(datetime.now())
        sl_id = f'{sl_tp_order_id_prefix}_b_sl'
        tp_id = f'{sl_tp_order_id_prefix}_b_tp'
        bo_id = f'{sl_tp_order_id_prefix}_b_bo'
        try:
            # Create a buy order with a stop loss and take profit
            stop_loss_order = self.client.new_order_test(
                symbol=symbol,
                side='SELL',
                type='STOP_MARKET',
                quantity=quantity,
                stopPrice=stop_loss,
                closePosition=True,
                timeInForce='GTC',
                newClientOrderId=sl_id
                
            )
            take_profit_order = self.client.new_order_test(
                symbol=symbol,
                side='SELL',
                type='TAKE_PROFIT_MARKET',
                quantity=quantity,
                stopPrice=take_profit,
                closePosition=True,
                timeInForce='GTC',
                newClientOrderId=tp_id
            )
            buy_order = self.client.new_order_test(
                symbol=symbol,
                side='BUY',
                type='LIMIT',
                quantity=quantity,
                price=entry_price,
                timeInForce='GTC',
                newClientOrderId=bo_id
            )
            self.trades.append((sl_id, tp_id, bo_id))
            logging.info(f"buy sl, tp: orders created: {stop_loss_order}, {take_profit_order}, {buy_order}")
        except Exception as e:
            logging.info(f"Error creating orders: {e}")

    def sell(self, symbol, stop_loss, take_profit, quantity, entry_price):
        sl_tp_order_id_prefix = self.get_unix_epoch_time_ms(datetime.now())
        sl_id = f'{sl_tp_order_id_prefix}_s_sl'
        tp_id = f'{sl_tp_order_id_prefix}_s_tp'
        bo_id = f'{sl_tp_order_id_prefix}_s_bo'
        try:
            # Create a sell order with a stop loss and take profit - I'm assuming it's the opposite of buy
            stop_loss_order = self.client.new_order_test(
                symbol=symbol,
                side='BUY',
                type='STOP_MARKET',
                quantity=quantity,
                stopPrice=stop_loss,
                closePosition=True,
                timeInForce='GTC',
                newClientOrderId=f'{sl_tp_order_id_prefix}_sl_s'
            )
            take_profit_order = self.client.new_order_test(
                symbol=symbol,
                side='BUY',
                type='TAKE_PROFIT_MARKET',
                quantity=quantity,
                stopPrice=take_profit,
                closePosition=True,
                timeInForce='GTC',
                newClientOrderId=f'{sl_tp_order_id_prefix}_tp_s'
            )
            buy_order = self.client.new_order_test(
                symbol=symbol,
                side='SELL',
                type='LIMIT',
                quantity=quantity,
                price=entry_price,
                timeInForce='GTC',
                newClientOrderId=f'{sl_tp_order_id_prefix}_bo_s'
            )
            self.trades.append((sl_id, tp_id, bo_id))
            logging.info(f"sell sl, tp: orders created: {stop_loss_order}, {take_profit_order}, {buy_order}")
        except ClientError as error:
            logging.info(f"Error creating sell sl, tp orders: {error}")  

    def cancel_order(self, symbol, order_id):
        try:
            response = self.client.cancel_order(
                symbol=symbol, orderId= order_id, recvWindow=2000
            )
            logging.info(f'Order cancelled: {response}')
        except ClientError as error:
            logging.info(
                "Found error. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message
                )
            )        

    def get_unix_epoch_time_ms(self, dt: datetime):
        """Converts a datetime object to unix epoch time in milliseconds"""
        unix_epoch_time_ms = int(dt.timestamp() * 1000)
        return unix_epoch_time_ms         


