from src.helpers.decorators import consumer_source
from src.stream_consumers.stream_consumer import StreamConsumer
from src.util import get_logger
from src.window.window import Window
from rx.subject import Subject
import rx.operators as op


@consumer_source(name='kline')
class Kline(StreamConsumer):
    """
    Need a reference to the window to access the data frames
    """

    col_mapping = {
        "t": "start_time",
        "T": "timestamp",
        "i": "interval",      
        "f": "first_trade_id",
        "L": "last_trade_id",
        "o": "open",  
        "c": "close",  
        "h": "high",  
        "l": "low",  
        "v": "volume",    
        "n": "number_of_trades",      
        "x": "is_closed",     
        "q": "quote_asset_volume",  
        "V": "taker_buy_asset_volume",     
        "Q": "taker_buy_quote_asset_volume",
        "s": "symbol"
    }
    def __init__(self, window: Window, main: Subject):
        super().__init__(window, main, self.col_mapping)
        super().subscribe({'interval': '1m'})
        self.window.add_consumer(self)
        self.logger = get_logger('Kline')
       
    def transform_message_dict(self, input_dict) -> dict:
        input_dict["k"]["s"] = input_dict["s"]
        if input_dict["k"]["x"] == True:
            return input_dict["k"]
        return None

    
            