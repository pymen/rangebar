from abc import ABC
import random
from typing import Tuple
from src.settings import get_settings
from src.util import get_logger
from src.window.window import Window
import pandas as pd
from rx.subject import Subject
import rx.operators as op


class SecondaryStreamConsumer(ABC):
    """
    Abstract class for level 2 stream consumers.
    Transforms events originating from the window class
    """

    def __init__(self, main: Subject) -> None:
        super().__init__()
        self.logger = get_logger('SecondaryStreamConsumer')
        self.main = main
       
    def get_consumer_df_name(self):
        snake_case = ""
        for char in self.__class__.__name__:
            if char.isupper():
                snake_case += "_" + char.lower()
            else:
                snake_case += char
        return snake_case.lstrip("_")    
            
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
            self.logger.info(f"create_series_from_dict: mapping: KeyError: {str(e)}")
            raise e
    
    
 

    

           
    