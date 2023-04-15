
from src.main import main
import time

def test_consume():
    window = main()
    time.sleep(1800)
    window.stop()