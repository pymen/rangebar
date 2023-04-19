from src.helpers.decorators import consumer_source, derived_frame_trigger
from src.stream_consumers.stream_consumer import StreamConsumer
from src.window.window import Window
import pandas as pd
import logging


@consumer_source(name='diff_book_depth')
class DiffBookBidAskSum(StreamConsumer):
    """
     https://binance-docs.github.io/apidocs/futures/en/#diff-book-depth-streams
    """
    col_mapping = {
        'e': 'event_type',
        'E': 'event_timestamp',
        'T': 'timestamp',
        's': 'symbol',
        'U': 'first_update_id_event',
        'u': 'final_update_id_event',
        'pu': 'previous_final_update_id_event',
        'b': 'total_bid_quantity',  # originally Bids to be updated
        'a': 'total_ask_quantity'  # originally Asks to be updated
    }

    def __init__(self, window: Window):
        super().__init__(window, self.col_mapping)
        super().subscribe({'speed': '500'})

    def transform_message_dict(self, input_dict) -> dict:
        input_dict["b"] = sum(float(x[1]) for x in input_dict["b"])
        input_dict["a"] = sum(float(x[1]) for x in input_dict["a"])
        return input_dict

    # FIXME: there are ordering checks that need to be done as described in the docs
    @derived_frame_trigger(df_name="diff_book_resample_30s", count=60)
    def diff_book_resample(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        This consumer receives a rows ever 500ms.  We want to resample the data at 30s intervals.
        """
        df_copy = df.drop(columns=["event_type", 'event_timestamp', "first_update_id_event",
                "final_update_id_event", "previous_final_update_id_event"]).copy()
        logging.info(f"diff_book_resample ~ resampled: df_copy.columns: {df_copy.columns}")
        resampled = df_copy.resample('30s').sum()
        logging.info("diff_book_resample ~ resampled", type(resampled))
        return resampled
