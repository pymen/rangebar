from src.helpers.util import get_strategy_parameters_max
from src.strategies.simple_strategy.simple_strategy_indicators import SimpleStrategyIndicators
from src.util import clear_logs, clear_symbol_windows, get_file_path
from tests.utils import test_logger

def test_get_file_path():
    settings = get_file_path('settings.json')
    print("test_get_file_path ~ settings", str(settings))

def test_logging():
    for i in range(0, 10):
        test_logger.info(f'logging test: {i}')  

def test_clear_logs():
    clear_logs()

def test_clear_symbol_windows():
    clear_symbol_windows()  

def test_get_strategy_parameters_max():
   max_win = get_strategy_parameters_max(SimpleStrategyIndicators)
   print(f'max_win: {max_win}')    

