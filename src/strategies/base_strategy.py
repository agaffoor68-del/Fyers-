from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any


class BaseStrategy(ABC):
    """Abstract base class for all trading strategies"""

    def __init__(self, name: str = "BaseStrategy"):
        self.name = name
        self.params = {}
        self.position = 0

    @abstractmethod
    def on_candle(self, candle, historical_data):
        """Called on each new candle"""
        pass

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals
        Returns dataframe with 'signal' column: 1 for buy, -1 for sell, 0 for hold
        """
        raise NotImplementedError("Either implement on_candle() or generate_signals()")

    def set_params(self, **params):
        """Set strategy parameters"""
        self.params.update(params)
        return self

    def get_params(self) -> Dict[str, Any]:
        """Get strategy parameters"""
        return self.params

    def __repr__(self):
        return f"{self.name}({self.params})"

