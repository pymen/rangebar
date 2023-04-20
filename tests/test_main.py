
from src.main import main
import time
from src.util import get_logger

logging = get_logger('tests')

def test_consume():
    window = main()
    time.sleep(1800)
    window.stop()