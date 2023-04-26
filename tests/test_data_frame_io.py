from src.data_frame_io.kline_data_frame_io import KlineDataFrameIO
from src.stream_consumers.primary_transformers.kline import Kline
from src.util import clear_logs, get_logger
from rx.subject import Subject # type: ignore

logging = get_logger('tests')

def test_kline_ingestion():
    clear_logs()
    primary = Subject()
    secondary = Subject()
    KlineDataFrameIO('kline', primary, secondary)
    kline = Kline(primary)
    kline.start()

