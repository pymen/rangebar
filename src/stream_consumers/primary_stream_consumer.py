from abc import ABC
import random
from src.helpers.dataclasses import DataFrameIOCommandEvent
from src.settings import get_settings
from src.util import get_logger
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from rx.subject import Subject # type: ignore
import pandas as pd
from typing import Any

class PrimaryStreamConsumer(ABC):
    """
    Abstract class for level 1 stream consumers.
    Transforms events originating from external sources
    """

    source_name: str
    def __init__(self, primary: Subject, col_mapping: dict[str, str]) -> None:
        super().__init__()
        settings = get_settings('bi')
        self.source_name = self.source_name
        self.ws_client = UMFuturesWebsocketClient(
            stream_url=settings['stream_url'])
        self.logger = get_logger('PrimaryStreamConsumer')
        self.primary = primary
        self.settings = get_settings('app')
        self.col_mapping = col_mapping
        self.df_name = self.get_consumer_df_name()
        self.logger.debug(f'df_name: {self.df_name}')

    def get_consumer_df_name(self) -> str:
        snake_case = ""
        for char in self.__class__.__name__:
            if char.isupper():
                snake_case += "_" + char.lower()
            else:
                snake_case += char
        return snake_case.lstrip("_")

    def subscribe(self, kwargs: dict[str, Any]) -> None:
        for symbol_config in self.settings['symbols_config']:
            symbol = symbol_config['symbol']
            self.logger.info(
                f"base_stream_consumer: subscribe: symbol: {symbol}")
            stream_id = random.randint(100, 999)
            kwargs['id'] = stream_id
            kwargs['symbol'] = symbol
            kwargs['callback'] = self.message_handler
            func = getattr(self.ws_client, self.source_name)
            try:
                func(**kwargs)
            except ValueError as ve:
                self.logger.info(f"A value error occurred: {ve}")
            except KeyError as ke:
                self.logger.info(f"A key error occurred: {ke}")
            except Exception as e:
                self.logger.info(f"An unknown error occurred: {e}")

    def message_handler(self, message: dict[str, str | int]) -> None:
        if 'result' not in message:
            try:
                output_dict: dict[str, str | int] | None = self.transform_message_dict(message)
                if output_dict is not None:
                    symbol, df_name, series = self.create_series_from_dict(output_dict)
                    event = DataFrameIOCommandEvent(method='append_row', df_name=df_name, kwargs={
                                         'symbol': symbol.lower(), 'row': series}) # type: ignore
                    self.logger.debug(f'event: {str(event)}')
                    self.primary.on_next(event)
            except Exception as e:
                self.logger.error("message_handler: ", str(e))
        else:
            self.logger.info(f"connection message: {message}")

    def create_series_from_dict(self, input_dict: dict[str, str | int]) -> tuple[str, str, Any]:
        self.logger.info(f"create_series_from_dict: {str(input_dict)}")
        try:
            # Map the dictionary keys to the desired column names using the col_mapping dictionary
            output_dict: dict[str, str | int] = {}
            for key, value in input_dict.items():
                if key in self.col_mapping:
                    output_dict[self.col_mapping[key]] = value
            # Create a pandas series using the updated dictionary
            output_series = pd.Series(output_dict)
            symbol_lower: str = input_dict['s'] # type: ignore
            return (symbol_lower, self.df_name, output_series)
        except KeyError as e:
            self.logger.info(
                f"create_series_from_dict: mapping: KeyError: {str(e)}")
            raise e

    def transform_message_dict(self, input_dict: dict[str, str | int]) -> dict[str, str | int] | None:
        """
        Called before mapping is applied to the input dictionary.
        """
        return input_dict

    def shutdown(self) -> None:
        self.ws_client.stop() # type: ignore

    def start(self) -> None:
        self.ws_client.start()
