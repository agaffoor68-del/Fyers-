from abc import ABC, abstractmethod


class BaseStrategy(ABC):
    def __init__(self):
        self.position = 0

    @abstractmethod
    def on_candle(self, candle, historical_data):
        pass
