from rx.subject import Subject
from src.stream_consumers.primary_transformers.account_orchestration import AccountOrchestration
from src.helpers.dataclasses import OrderStatusEvent
from src.util import get_logger
from tests.utils import read_from_tests_out_json_to_dict
import asyncio
import pytest
import time

logging = get_logger('tests')

def new_instance():
    main = Subject()
    order_orchestration = AccountOrchestration(main)
    return order_orchestration, main

def test_parse_order_trade_update():
    target, main = new_instance()
    raw_message = read_from_tests_out_json_to_dict('user_data_mapping/ORDER_TRADE_UPDATE.json')
    print(f'raw_message: {raw_message}')
    target.get_user_data_stream().subscribe(lambda x: print(x))
    main.on_next(OrderStatusEvent(
                    symbol='BTCUSDT', payload_type='ws', payload=raw_message))