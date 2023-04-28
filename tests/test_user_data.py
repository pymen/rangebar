
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from rx.subject import Subject # type: ignore
from src.helpers.dataclasses import OrderStatusEvent
from src.stream_consumers.exchange.user_data import UserData
from tests.utils import read_from_tests_out_json_to_dict, write_to_tests_out_file
import asyncio
import pytest
import time


def new_instance():
    main = Subject()
    order_status = UserData(main)
    return order_status, main


def test_get_exchange_info():
    target, _ = new_instance()
    resp = target.get_exchange_info()
    import json
    # convert the dictionary to a JSON string with indentation
    json_str = json.dumps(resp, indent=4)
    write_to_tests_out_file(json_str, 'exchange_info.json')

@pytest.mark.asyncio
async def test_poll():
    target, main = new_instance()
    await main.subscribe(lambda x: print(x))
    try:
        await target.poll()
    except Exception as e:
        print(f"Polling failed with exception: {e}")
    finally:
        target.kill_polling = True
    await asyncio.sleep(30)


@pytest.mark.asyncio
async def test_subscribe_to_user_stream():
    import json
    from pathlib import Path
    target, main = new_instance()
    cwd = Path.cwd()
    dir_path = cwd.joinpath('tests/out')
    filename = dir_path.joinpath(filename)
    with open('user_data.json', 'a') as f:
        # Subscribe to the data stream
        main.subscribe(lambda x: f.write(json.dumps(x) + '\n'))
    await target.subscribe_to_user_stream()
    await asyncio.sleep(360)
    
def test_get_balance():
    target, _ = new_instance()
    resp = target.get_balance()
    import json
    # convert the dictionary to a JSON string with indentation
    json_str = json.dumps(resp, indent=4)
    write_to_tests_out_file(json_str, 'get_balance.json')

def test_parse_order_trade_update():
    target, main = new_instance()
    raw_message = read_from_tests_out_json_to_dict('user_data_mapping/ORDER_TRADE_UPDATE.json')
    print(f'raw_message: {raw_message}')
    target.get_user_data_stream().subscribe(lambda x: print(x))
    main.on_next(OrderStatusEvent(
                    symbol='BTCUSDT', payload_type='ws', payload=raw_message))

    




