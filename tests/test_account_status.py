from src.strategies.account_status import AccountStatus
from src.window.window import Window
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from rx.subject import Subject
from src.main import stream_url
from tests.utils import init_logging, write_to_tests_out_file
import asyncio
import pytest

def new_instance():
    init_logging()
    order_status_subject = Subject()
    window = Window(UMFuturesWebsocketClient(stream_url=stream_url), Subject(), Subject())
    order_status = AccountStatus(window, order_status_subject)
    return order_status, order_status_subject


def test_get_exchange_info():
    target, _ = new_instance()
    resp = target.get_exchange_info()
    import json
    # convert the dictionary to a JSON string with indentation
    json_str = json.dumps(resp, indent=4)
    write_to_tests_out_file(json_str, 'exchange_info.json')

@pytest.mark.asyncio
async def test_poll():
    target, order_status_subject = new_instance()
    order_status_subject.subscribe(lambda x: print(x))
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

    




