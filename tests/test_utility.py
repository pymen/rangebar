from src.util import clear_logs, clear_symbol_windows, get_file_path, get_logger

def test_get_file_path():
    settings = get_file_path('settings.json')
    print("test_get_file_path ~ settings", str(settings))

def test_logging():
    logger = get_logger('JustinRobinsonDreamer')
    for i in range(0, 10):
        logger.info(f'logging test: {i}')  

def test_clear_logs():
    clear_logs()

def test_clear_symbol_windows():
    clear_symbol_windows()          
