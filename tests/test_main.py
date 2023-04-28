
from src.main import start, stop
import time

def test_run() -> None:
    start()
    time.sleep(1800)
    stop()