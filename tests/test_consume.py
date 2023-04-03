
from src.consume import consume
import time

def test_consume():
    window = consume()
    time.sleep(1800)
    window.stop()