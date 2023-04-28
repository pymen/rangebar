from src.io.kline_io import KlineIO
from src.io.range_bar_io import RangeBarIO
from src.fetch_historical.historical_kline import HistoricalKline
from src.stream_consumers.exchange.kline import Kline
from src.stream_consumers.rig.range_bars import RangeBar
from src.util import clear_logs, clear_symbol_windows, get_logger
from rx.subject import Subject # type: ignore

logging = get_logger('tests')

def test_kline_ingestion() -> None:
    clear_logs()
    clear_symbol_windows()
    primary = Subject()
    KlineIO(primary)
    HistoricalKline(primary)
    kline = Kline(primary)
    RangeBar(primary)
    RangeBarIO(primary)
    kline.start()

