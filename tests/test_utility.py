from dataclasses import dataclass
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

@dataclass
class Test1:
    name: str

@dataclass
class Test2(Test1):
    name: str  

@dataclass
class Test3(Test1):
    name: str  


def test_instance_of_inheritance():
    t1 = Test1('test1')
    t2 = Test2('test2')
    t3 = Test3('test3')
    if isinstance(t2, Test1):
        print('t2 is Test1')
    if isinstance(t3, Test1):
        print('t3 is Test1') 
    if isinstance(t1, Test2):
        print('t1 is Test2')
    else:
        print('t1 is not Test2')              

