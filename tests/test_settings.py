from src.settings import get_settings
from src.util import get_logger

logging = get_logger('tests')

def test_get_settings():
    settings = get_settings('app')
    print("settings",settings)
    keys = settings.keys()
    for key in ['window', 'symbols', 'streamNames']:
        assert key in keys
    
    