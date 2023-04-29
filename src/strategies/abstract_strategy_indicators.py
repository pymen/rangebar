

from abc import ABC, abstractmethod
from typing import Callable
import pandas as pd


class AbstractStrategyIndicators(ABC):
    """
    Abstract class for strategies that use indicators.
    Singleton
    """
    instance = None
    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def get_indicators_min_window_size(self) -> int:
        parameters: list[int] = []
        for attr in dir(self):
            if attr.startswith('p_'):
                p = getattr(self, attr)
                parameters.append(p)
        return max(parameters) * 10

    @abstractmethod
    def get_processors(self) -> list[Callable[[pd.DataFrame], pd.DataFrame]]:
        pass