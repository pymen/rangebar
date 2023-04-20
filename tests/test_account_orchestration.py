from rx.subject import Subject
from src.account_admin.account_orchestration import AccountOrchestration
from src.helpers.dataclasses import OrderStatusEvent
from src.util import get_logger
from tests.utils import read_from_tests_out_json_to_dict
import asyncio
import pytest
import time

logging = get_logger('tests')

def new_instance():
    account_data_stream = Subject()
    order_orchestration = AccountOrchestration(account_data_stream)
    return order_orchestration, account_data_stream

def test_parse_order_trade_update():
    target, account_data_stream = new_instance()
    raw_message = read_from_tests_out_json_to_dict('user_data_mapping/ORDER_TRADE_UPDATE.json')
    print(f'raw_message: {raw_message}')
    target.get_user_data_stream().subscribe(lambda x: print(x))
    account_data_stream.on_next(OrderStatusEvent(
                    symbol='BTCUSDT', payload_type='ws', payload=raw_message))