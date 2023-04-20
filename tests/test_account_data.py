
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from rx.subject import AsyncSubject
from src.account_admin.account_data import AccountData
from tests.utils import init_logging, write_to_tests_out_file
import asyncio
import pytest
import time

def new_instance():
    init_logging()
    account_data_stream = AsyncSubject()
    order_status = AccountData(account_data_stream)
    return order_status, account_data_stream


def test_get_exchange_info():
    target, _ = new_instance()
    resp = target.get_exchange_info()
    import json
    # convert the dictionary to a JSON string with indentation
    json_str = json.dumps(resp, indent=4)
    write_to_tests_out_file(json_str, 'exchange_info.json')

@pytest.mark.asyncio
async def test_poll():
    target, account_data_stream = new_instance()
    await account_data_stream.subscribe(lambda x: print(x))
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
    target, account_data_stream = new_instance()
    cwd = Path.cwd()
    dir_path = cwd.joinpath('tests/out')
    filename = dir_path.joinpath(filename)
    with open('user_data.json', 'a') as f:
        # Subscribe to the data stream
        account_data_stream.subscribe(lambda x: f.write(json.dumps(x) + '\n'))
    await target.subscribe_to_user_stream()
    await asyncio.sleep(360)
    
def test_get_balance():
    target, _ = new_instance()
    resp = target.get_balance()
    import json
    # convert the dictionary to a JSON string with indentation
    json_str = json.dumps(resp, indent=4)
    write_to_tests_out_file(json_str, 'get_balance.json')    

    




