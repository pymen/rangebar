from src.helpers.dataclasses import FetchHistoricalEvent
from src.stream_consumers.transformers.kline import Kline
from src.window.window import Window
from rx.core import operators as op

class HistoricalKline:

    transformer: Kline
    def __init__(self, window: Window):
         self.transformer = Kline(window)
         window.historical.pipe(op.filter(lambda e: e.source == 'kline'), op.map(self.fetch_historical)).subscribe()


    def fetch_historical(self, e: FetchHistoricalEvent):
        """
        Fetches historical kline from the last_timestamp in the event and calls
        window.append_rows function which will eval_triggers eg: in the case where
        a derived source such as range bars published the FetchHistoricalEvent the
        missing source data will be there for it to continue. The time elapsed may 
        need to be adjusted depending on how long this takes
        """
        pass    
                     