from abc import ABC
import random
from typing import Tuple
from src.settings import get_settings
from src.window.window import Window
import pandas as pd
import logging

class StreamConsumer(ABC):

    def __init__(self, window: Window, col_mapping: dict, primary_df_name: str = None) -> None:
        super().__init__()
        self.window = window
        self.settings = get_settings('app')
        self.col_mapping = col_mapping
        if primary_df_name is not None:
            self.df_name = primary_df_name
        else:    
            self.df_name = self.get_consumer_df_name()
        self.window.add_consumer(self)

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
            logging.info(f"base_stream_consumer: subscribe: symbol: {symbol}, stream_name: {self.source_name}")
            stream_id = random.randint(100, 999)
            kwargs['id'] = stream_id
            kwargs['symbol'] = symbol
            kwargs['callback'] = self.message_handler
            func = getattr(self.window.ws_client, self.source_name)
            try:
                func(**kwargs)
            except ValueError as ve:
                logging.info(f"A value error occurred: {ve}")
            except KeyError as ke:
                logging.info(f"A key error occurred: {ke}")
            except Exception as e:
                logging.info(f"An unknown error occurred: {e}")
   
                
    def message_handler(self, message):
        if 'result' not in message:
            try:
                symbol, df_name, series = self.create_series_from_dict(message)
                self.window.append_row(symbol.lower(), df_name, series, self.index_cols)
            except Exception as e:
                # FIXME error thrown
                logging.info("message_handler ~ e: ",str(e))    
        else:
            logging.info(f"connection message: {message}")
            
    def create_series_from_dict(self, input_dict) -> Tuple:
        # logging.info(f"base_stream_consumer: create_series_from_dict")
        # Prepare the data
        input_dict = self.transform_message_dict(input_dict)
        if input_dict is not None:
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
                logging.info(f"create_series_from_dict: mapping: KeyError: {str(e)}")
                raise e  
       
    def transform_message_dict(self, input_dict) -> dict:
        """
        Called before mapping is applied to the input dictionary.
        """
        return input_dict
    
    
 

    

           
    