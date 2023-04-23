
from src.account_admin.user_data_stream import AccountData
from src.stream_consumers.primary_transformers.user_data import UserData
from src.fetch_historical.historical_kline import HistoricalKline
from src.settings import get_settings
from src.strategies.order_client import OrderClient
from src.strategies.simple_strategy.indicators import SimpleStrategyIndicators
from src.strategies.simple_strategy.strategy import SimpleStrategy
from src.stream_consumers.secondary_transformers.range_bars import RangeBar
from src.util import get_logger
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
    main = Subject()
    """
    Window
    """
    ws_client = UMFuturesWebsocketClient(stream_url=settings['stream_url'])
    window = Window(ws_client, main)
    """
    Transformers

    Need a reference to the window to access the data frames
    """
    # DiffBookBidAskSum(window, window)
    # Kline(window, window)
    RangeBar(window, main)
    """
    Historical
    """
    HistoricalKline(main)
    """
    Indicators
    """
    SimpleStrategyIndicators(main)
    """
    Strategies
    """
    client: OrderClient = OrderClient()
    SimpleStrategy(main)
    """
    Account
    """
    AccountData(main)
    UserData(client, main)
    """"""
    window.start()
    return window
         
    