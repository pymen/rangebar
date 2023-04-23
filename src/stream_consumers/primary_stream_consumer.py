from abc import ABC
import random
from typing import Tuple
from src.helpers.dataclasses import DataFrameIOCommandEvent
from src.settings import get_settings
from src.util import get_logger
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
import pandas as pd
from rx.subject import Subject


class PrimaryStreamConsumer(ABC):
    """
    Abstract class for level 1 stream consumers.
    Transforms events originating from external sources
    """

    def __init__(self, primary: Subject, col_mapping: dict) -> None:
        super().__init__()
        settings = get_settings('bi')
        self.ws_client = UMFuturesWebsocketClient(
            stream_url=settings['stream_url'])
        self.logger = get_logger('PrimaryStreamConsumer')
        self.primary = primary
        self.settings = get_settings('app')
        self.col_mapping = col_mapping
        self.df_name = self.get_consumer_df_name()

    def get_consumer_df_name(self):
        snake_case = ""
        for char in self.__class__.__name__:
            if char.isupper():
                snake_case += "_" + char.lower()
            else:
                snake_case += char
        return snake_case.lstrip("_")

    def subscribe(self, kwargs: dict):
        for symbol_config in self.settings['symbols_config']:
            symbol = symbol_config['symbol']
            self.logger.info(
                f"base_stream_consumer: subscribe: symbol: {symbol}, stream_name: {self.source_name}")
            stream_id = random.randint(100, 999)
            kwargs['id'] = stream_id
            kwargs['symbol'] = symbol
            kwargs['callback'] = self.message_handler
            func = getattr(self.window.ws_client, self.source_name)
            try:
                func(**kwargs)
            except ValueError as ve:
                self.logger.info(f"A value error occurred: {ve}")
            except KeyError as ke:
                self.logger.info(f"A key error occurred: {ke}")
            except Exception as e:
                self.logger.info(f"An unknown error occurred: {e}")

    def message_handler(self, message):
        if 'result' not in message:
            try:
                output_dict = self.transform_message_dict(message)
                if output_dict is not None:
                    symbol, df_name, series = self.create_series_from_dict(
                        output_dict)
                    self.primary.on_next(DataFrameIOCommandEvent(method='append_row', kwargs={
                                         'symbol': symbol.lower(), 'df_name':  df_name, 'series': series, 'index_cols': self.index_cols}))
            except Exception as e:
                self.logger.error("message_handler: ", str(e))
        else:
            self.logger.info(f"connection message: {message}")

    def create_series_from_dict(self, input_dict: dict) -> Tuple:
        self.logger.info(f"create_series_from_dict: {str(input_dict)}")
        try:
            # Map the dictionary keys to the desired column names using the col_mapping dictionary
            output_dict = {}
            for key, value in input_dict.items():
                if key in self.col_mapping:
                    output_dict[self.col_mapping[key]] = value
            # Create a pandas series using the updated dictionary
            output_series = pd.Series(output_dict)
            return (input_dict['s'].lower(), self.df_name, output_series)
        except KeyError as e:
            self.logger.info(
                f"create_series_from_dict: mapping: KeyError: {str(e)}")
            raise e

    def transform_message_dict(self, input_dict) -> dict:
        """
        Called before mapping is applied to the input dictionary.
        """
        return input_dict

    def shutdown(self):
        self.ws_client.stop()

    def start(self):
        self.ws_client.start()
