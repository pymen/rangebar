from src.util import get_file_path, get_logger

def test_get_file_path():
    settings = get_file_path('settings.json')
    print("test_get_file_path ~ settings", str(settings))

def test_logging():
    test_log_path = str(get_file_path('logs/debug.log').absolute())
    print(f'test_log_path: {test_log_path}')
    logger = get_logger('JustinRobinsonNutter')
    logger.info("test_logging ~ info")
    logger.debug("test_logging ~ debug")
    logger.warning("test_logging ~ warning")
    logger.error("test_logging ~ error")
    logger.critical("test_logging ~ critical")    
