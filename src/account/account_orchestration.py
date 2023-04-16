import logging
from rx.subject import Subject
from src.strategies.order_client import OrderClient

class AccountOrchestration:
    """
    The responsibility of this to orchestrate the order cancellation, 
    in the case of a take profit or stop loss orders.
    Also in the case of impending liquidation.

    https://binance-docs.github.io/apidocs/futures/en/#position-information-v2-user_data
    """

    def __init__(self, order_client: OrderClient, account_data_stream: Subject):
        pass