from src.helpers.decorators import consumer_source
from src.stream_consumers.stream_consumer import StreamConsumer
from src.window.window import Window

@consumer_source(name='kline')
class Kline(StreamConsumer):

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
    def __init__(self, window: Window):
        super().__init__(window, self.col_mapping)
        super().subscribe({'interval': '1m'})

    def transform_message_dict(self, input_dict) -> dict:
        input_dict["k"]["s"] = input_dict["s"]
        return input_dict["k"]    
                
            