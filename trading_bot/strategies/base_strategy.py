from abc import ABC, abstractmethod
import pandas as pd

class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.

    Each strategy must implement the check_signal method, which takes
    a pandas DataFrame of OHLCV data and returns a signal ('BUY', 'SELL', or 'HOLD').
    """

    def __init__(self, name: str, params: dict = None):
        """
        Initializes the strategy with a name and optional parameters.

        :param name: The display name of the strategy.
        :param params: A dictionary of parameters to configure the strategy (e.g., periods for moving averages).
        """
        self.name = name
        self.params = params if params is not None else {}

    @abstractmethod
    def check_signal(self, ohlcv_data: pd.DataFrame) -> str:
        """
        The core logic of the strategy. Analyzes the data and returns a signal.

        :param ohlcv_data: A pandas DataFrame with columns ['Open', 'High', 'Low', 'Close', 'Volume'].
                           The index should be a DatetimeIndex.
        :return: A string signal: 'BUY', 'SELL', or 'HOLD'.
        """
        pass

    def __str__(self):
        return f"Strategy(name='{self.name}', params={self.params})"
