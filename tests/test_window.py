

from src.settings import get_settings
from src.stream_consumers.primary_transformers.diff_book_bid_ask_sum import DiffBookBidAskSum
from src.stream_consumers.secondary_transformers.range_bars import RangeBar
from src.util import get_logger
from src.window.window import Window
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from rx.subject import Subject
import rx.operators as op
from src.helpers.dataclasses import WindowCommandEvent
import pandas as pd

logging = get_logger('tests')


def new_instance():
    settings = get_settings('bi')
    ws_client = UMFuturesWebsocketClient(stream_url=settings['stream_url'])
    window = Window(ws_client, Subject())
    return window


def test_window_logging():
    window = new_instance()
    for i in range(0, 10):
        window.logger.info(f'logging test: {i}')


def test_window_start_init():
    window = new_instance()
    assert window is not None
    print("window.symbol_dict_df_dict: ", window.symbol_df_dict)


def test_window_start():
    window = new_instance()
    window.start()


def test_get_symbol_grouped_csv_paths():
    window = new_instance()
    window.get_df_names_from_csv_paths()


def test_get_consumer_triggers():
    window = new_instance()
    RangeBar(window)
    symbol = get_settings('app')['symbols_config'][0]['symbol']
    consumer_dict = window.consumers[symbol]
    triggers = []
    for _, consumer in consumer_dict.items():
        triggers = window.get_consumer_triggers(consumer)
        break
    assert len(triggers) > 0


def test_consumer_derived_frame_trigger_decorator():
    window = new_instance()
    rbc = RangeBar(window)
    triggers = window.get_consumer_triggers(rbc)
    print(f'triggers: {len(triggers)}')
    assert len(triggers) > 0


class Test1:

    def __init__(self, main):
        self.main = main

    def init_subscriptions(self):
        self.main.pipe(
            op.filter(lambda o: isinstance(o, WindowCommandEvent)),
            op.map(lambda e: getattr(self, e.method)(**e.kwargs))
        ).subscribe()

    def append_rows(self, symbol: str, df_name: str, df_section: pd.DataFrame):
        print(
            f'append_rows: {symbol} {df_name},  df_section:\n{str(df_section)}')


def test_command_event():
    main = Subject()
    Test1(main).init_subscriptions()
    df = pd.DataFrame({'column1': [1, 2, 3], 'column2': [
                      'a', 'b', 'c'], 'column3': [True, False, True]})
    main.on_next(WindowCommandEvent(method='append_rows', kwargs={
                 'symbol': 'x', 'df_name': 'kline', 'df_section': df}))
