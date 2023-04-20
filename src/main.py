from src.account_admin.account_data import AccountData
from src.account_admin.account_orchestration import AccountOrchestration
from src.fetch_historical.historical_kline import HistoricalKline
from src.settings import get_settings
from src.strategies.order_client import OrderClient
from src.strategies.simple_strategy.indicators import SimpleStrategyIndicators
from src.strategies.simple_strategy.strategy import SimpleStrategy
from src.stream_consumers.transformers.range_bars import RangeBar
from src.utility import get_file_path
from src.window.window import Window
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from rx.subject import AsyncSubject
import logging
# logging.basicConfig(filename=get_file_path('data/logs/debug.log'), encoding='utf-8', level=logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)
# The REST baseurl for testnet is "https://testnet.binancefuture.com"
# The Websocket baseurl for testnet is "wss://stream.binancefuture.com"


def main() -> Window:
    settings = get_settings('bi')
    """
    Event Subjects
    """
    calc_indicators = AsyncSubject()
    next_bar = AsyncSubject()
    historical = AsyncSubject()
    account_data_stream = AsyncSubject()
    """
    Window
    """
    ws_client = UMFuturesWebsocketClient(stream_url=settings['stream_url'])
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
    AccountData(account_data_stream)
    AccountOrchestration(client, account_data_stream)
    """"""
    window.start()
    return window
         
    