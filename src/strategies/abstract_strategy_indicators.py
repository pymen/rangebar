

from abc import ABC, abstractmethod
from typing import Callable
import pandas as pd


class AbstractStrategyIndicators(ABC):

    @abstractmethod
    def get_processors(self) -> list[Callable[[pd.DataFrame], pd.DataFrame]]:
        pass