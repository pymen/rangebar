from src.fetch_historical.historical_kline import HistoricalKline
from src.strategies.simple_strategy.indicators import SimpleStrategyIndicators
from src.strategies.simple_strategy.strategy import SimpleStrategy
from src.stream_consumers.transformers.range_bars import RangeBar
from src.window.window import Window
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from rx.core import Subject

def consume() -> Window:
    """
    Event Subjects
    """
    calc_indicators = Subject()
    next_bar = Subject()
    historical = Subject()
    """
    Window
    """
    ws_client = UMFuturesWebsocketClient()
    window = Window(ws_client, calc_indicators, historical)
    # Transformers
    # DiffBookBidAskSum(window)
    # Kline(window)
    RangeBar(window)
    """
    Historical
    """
    HistoricalKline(window)
    """
    Indicators
    """
    SimpleStrategyIndicators(calc_indicators, next_bar)
    """
    Strategies
    """
    SimpleStrategy(next_bar)
    window.start()
    return window
         
    