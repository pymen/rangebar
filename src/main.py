from src.account.account_data import AccountData
from src.account.account_orchestration import AccountOrchestration
from src.fetch_historical.historical_kline import HistoricalKline
from src.strategies.order_client import OrderClient
from src.strategies.simple_strategy.indicators import SimpleStrategyIndicators
from src.strategies.simple_strategy.strategy import SimpleStrategy
from src.stream_consumers.transformers.range_bars import RangeBar
from src.utility import get_file_path
from src.window.window import Window
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from rx.subject import Subject
import logging
logging.basicConfig(filename=get_file_path('data/logs/debug.log'), encoding='utf-8', level=logging.DEBUG)

# The REST baseurl for testnet is "https://testnet.binancefuture.com"
# The Websocket baseurl for testnet is "wss://stream.binancefuture.com"
stream_url='wss://stream.binancefuture.com'
base_url='https://testnet.binancefuture.com'

def main() -> Window:
    """
    Event Subjects
    """
    calc_indicators = Subject()
    next_bar = Subject()
    historical = Subject()
    account_data_stream = Subject()
    """
    Window
    """
    ws_client = UMFuturesWebsocketClient(stream_url=stream_url)
    window = Window(ws_client, calc_indicators, historical)
    """
    Transformers
    """
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
    client: OrderClient = OrderClient()
    SimpleStrategy(client, next_bar)
    """
    Account
    """
    AccountData(window, account_data_stream)
    AccountOrchestration(client, account_data_stream)
    """"""
    window.start()
    return window
         
    