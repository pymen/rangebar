
from src.main import start, stop
import time
from src.util import get_logger

logging = get_logger('tests')

def test_run() -> None:
    start()
    time.sleep(1800)
    stop()