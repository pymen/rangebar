from src.strategies.simple_strategy.indicators import SimpleStrategyIndicators
from src.strategies.simple_strategy.strategy import SimpleStrategy
from src.stream_consumers.transformers.diff_book_bid_ask_sum import DiffBookBidAskSum
from src.stream_consumers.transformers.kline import Kline
from src.stream_consumers.transformers.range_bars import RangeBar
from src.window.window import Window
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from rx.core import Subject


def consume() -> Window:
    # Event Subjects
    calc_indicators = Subject()
    next_bar = Subject()
    # Window
    ws_client = UMFuturesWebsocketClient()
    window = Window(ws_client, calc_indicators)
    # Transformers
    # DiffBookBidAskSum(window)
    # Kline(window)
    RangeBar(window)
    #  Indicators
    SimpleStrategyIndicators(calc_indicators, next_bar)
    # Strategies
    SimpleStrategy(next_bar)
    window.start()
    return window
         
    