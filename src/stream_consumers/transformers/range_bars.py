from typing import Dict
import pandas as pd
from src.settings import get_settings
from src.helpers.decorators import consumer_source, derived_frame_trigger, config
from src.stream_consumers.stream_consumer import StreamConsumer
from src.window.window import Window
from src.helpers.range_bars import create_range_bar_df

@consumer_source(name='kline', df_index=['timestamp', 'last_trade_id'])
class RangeBar(StreamConsumer):

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

    @derived_frame_trigger(df_name="range_bars", count=1)
    def create_range_bar_df(self, df: pd.DataFrame, symbol_config: Dict[str, str] = None) -> pd.DataFrame:
        if symbol_config['range']['average_adr'] is None:
            raise ValueError("Range size is not set for symbol: {}".format(symbol_config['symbol']))
        average_adr = float(symbol_config['range']['average_adr'])
        return create_range_bar_df(df, average_adr)
        
            