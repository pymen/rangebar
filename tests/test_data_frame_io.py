from src.data_frame_io.kline_data_frame_io import KlineDataFrameIO
from src.fetch_historical.historical_kline import HistoricalKline
from src.stream_consumers.primary_transformers.kline import Kline
from src.stream_consumers.secondary_transformers.range_bars import RangeBar
from src.util import clear_logs, clear_symbol_windows, get_logger
from rx.subject import Subject # type: ignore

logging = get_logger('tests')

def test_kline_ingestion() -> None:
    clear_logs()
    clear_symbol_windows()
    primary = Subject()
    secondary = Subject()
    KlineDataFrameIO('kline', primary)
    HistoricalKline(primary)
    kline = Kline(primary)
    RangeBar(primary)
    kline.start()

