from src.stream_consumers.primary_transformers.kline import Kline
from src.stream_consumers.primary_transformers.user_data import UserData
from src.fetch_historical.historical_kline import HistoricalKline
from src.strategies.simple_strategy.indicators import SimpleStrategyIndicators
from src.strategies.simple_strategy.strategy import SimpleStrategy
from src.stream_consumers.secondary_transformers.range_bars import RangeBar
from src.util import get_logger
from src.window.window import Window
from rx.subject import Subject

# The REST baseurl for testnet is "https://testnet.binancefuture.com"
# The Websocket baseurl for testnet is "wss://stream.binancefuture.com"
logger = get_logger('main')

def setup():
    """
    Event Subjects
    """
    primary = Subject()
    secondary = Subject()
    """
    Transformers
    """
    """
    Primary Consumers & Transformers
    """
    kline = Kline(primary, secondary)
    user_date = UserData(primary, secondary)
    """
    Secondary Consumers & Transformers
    """
    range_bar = RangeBar(primary, secondary)
    """
    Window
    """
    Window('kline', primary, secondary)
    Window('range_bar', primary, secondary)
    Window('user_data', primary, secondary)
    """
    Historical
    """
    HistoricalKline(primary)
    """
    Indicators
    """
    SimpleStrategyIndicators(secondary)
    """
    Strategies
    """
    SimpleStrategy(secondary)
    return kline, user_date, range_bar

consumers: tuple[Kline, UserData, RangeBar] = None
def start():
    global consumers
    consumers = setup()
    for consumer in consumers:
        consumer.start()

def stop():
    for consumer in consumers:
        consumer.stop()

    
    
         
    