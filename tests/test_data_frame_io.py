from src.stream_consumers.primary_transformers.kline import Kline
from src.util import get_logger
from src.data_source.data_frame_io import DataFrameIO
from rx.subject import Subject
import time

logging = get_logger('tests')


def new_instance(df_name):
    primary = Subject()
    secondary = Subject()
    data_frame_io = DataFrameIO(df_name, primary, secondary)
    return primary, secondary, data_frame_io


def test_window_logging():
    _, _, data_frame_io = new_instance()
    for i in range(0, 10):
        data_frame_io.logger.info(f'logging test: {i}')


def test_kline_ingestion():
    primary, secondary, data_frame_io = new_instance('kline')
    data_frame_io.init_subscriptions()
    kline = Kline(primary, secondary)
    kline.start()
    time.sleep(120)
    kline.stop()
