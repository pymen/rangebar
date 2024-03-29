from typing import Any
from src.helpers.decorators import consumer_source
from src.stream_consumers.exchange_stream_consumer import ExchangeStreamConsumer
from src.util import get_logger
from rx.subject import Subject # type: ignore

@consumer_source(source_name='kline')
class Kline(ExchangeStreamConsumer):
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
    def __init__(self, primary: Subject):
        super().__init__(primary, self.col_mapping)
        super().subscribe({'interval': '1m'})
        self.logger = get_logger(self)
        
       
    def transform_message_dict(self, input_dict: Any) -> dict[str, str | int] | None:
        input_dict["k"]["s"] = input_dict["s"]
        if input_dict["k"]["x"] == True:
            return input_dict["k"]
        return None

    
            