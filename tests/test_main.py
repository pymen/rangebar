
from src.io.kline_io import KlineIO
from src.io.range_bar_io import RangeBarIO
from src.fetch_historical.historical_kline import HistoricalKline
from src.strategies.simple_strategy.simple_strategy_indicators import SimpleStrategyIndicators
from src.stream_consumers.exchange.kline import Kline
from src.stream_consumers.rig.range_bars import RangeBar
from src.util import clear_logs, clear_symbol_windows
from rx.subject import Subject # type: ignore

def test_run() -> None:
    clear_logs()
    clear_symbol_windows()
    primary = Subject()
    KlineIO(primary)
    HistoricalKline(primary)
    RangeBar(primary)
    RangeBarIO(primary)
    SimpleStrategyIndicators(primary)
    Kline(primary).start()