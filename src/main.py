from multiprocessing import get_logger
from src.account_admin.account_data import AccountData
from src.account_admin.account_orchestration import AccountOrchestration
from src.fetch_historical.historical_kline import HistoricalKline
from src.settings import get_settings
from src.strategies.order_client import OrderClient
from src.strategies.simple_strategy.indicators import SimpleStrategyIndicators
from src.strategies.simple_strategy.strategy import SimpleStrategy
from src.stream_consumers.transformers.range_bars import RangeBar
from src.window.window import Window
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from rx.subject import Subject

# The REST baseurl for testnet is "https://testnet.binancefuture.com"
# The Websocket baseurl for testnet is "wss://stream.binancefuture.com"
logger = get_logger('main')

def main() -> Window:
    settings = get_settings('bi')
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
         
    