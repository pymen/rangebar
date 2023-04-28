from src.util import get_settings
from tests.utils import test_logger

def test_get_settings():
    settings = get_settings('app')
    test_logger.debug(f"settings: {settings}")
    
    