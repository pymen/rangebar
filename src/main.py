from src.data_frame_io.kline_data_frame_io import KlineDataFrameIO
from src.data_frame_io.range_bar_data_frame_io import RangeBarDataFrameIO
from src.stream_consumers.primary_transformers.kline import Kline
from src.stream_consumers.primary_transformers.user_data import UserData
from src.fetch_historical.historical_kline import HistoricalKline
from src.strategies.simple_strategy.simple_strategy_indicators import SimpleStrategyIndicators
from src.strategies.simple_strategy.smiple_strategy import SimpleStrategy
from src.stream_consumers.secondary_transformers.range_bars import RangeBar
from src.util import get_logger
from rx.subject import Subject # type: ignore

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
    kline = Kline(primary)
    user_date = UserData(primary)
    """
    Secondary Consumers & Transformers
    """
    range_bar = RangeBar(primary, secondary)
    """
    Data Frame IO
    """
    KlineDataFrameIO('kline', primary, secondary)
    RangeBarDataFrameIO('range_bar', primary, secondary)
    # DataFrameIO('user_data', primary, secondary)
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

consumers = setup()
def start():
    global consumers
    for consumer in consumers:
        consumer.start() # type: ignore

def stop():
    global consumers
    for consumer in consumers:
        consumer.stop() # type: ignore

    
    
         
    