
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from rx.subject import Subject
from src.account.account_data import AccountData
from tests.utils import init_logging, write_to_tests_out_file
import asyncio
import pytest

def new_instance():
    init_logging()
    account_data_stream = Subject()
    order_status = AccountData(account_data_stream)
    account_data_stream.subscribe(lambda x: print(x))
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
    account_data_stream.subscribe(lambda x: print(x))
    try:
        await target.poll()
    except Exception as e:
        print(f"Polling failed with exception: {e}")
    finally:
        target.kill_polling = True
    await asyncio.sleep(30)
    
def test_get_balance():
    target, _ = new_instance()
    resp = target.get_balance()
    import json
    # convert the dictionary to a JSON string with indentation
    json_str = json.dumps(resp, indent=4)
    write_to_tests_out_file(json_str, 'get_balance.json')    

    




