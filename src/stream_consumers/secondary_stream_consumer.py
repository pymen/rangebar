from abc import ABC
from typing import Tuple
from src.util import get_logger
import pandas as pd
from rx.subject import Subject # type: ignore
import rx.operators as op


class SecondaryStreamConsumer(ABC):
    """
    Abstract class for level 2 stream consumers.
    Transforms events originating from the window class
    """

    def __init__(self, primary: Subject, secondary: Subject) -> None:
        super().__init__()
        self.logger = get_logger('SecondaryStreamConsumer')
        self.primary = primary
        self.secondary = secondary
       
    def get_consumer_df_name(self) -> str:
        snake_case = ""
        for char in self.__class__.__name__:
            if char.isupper():
                snake_case += "_" + char.lower()
            else:
                snake_case += char
        return snake_case.lstrip("_")
    
    
 

    

           
    