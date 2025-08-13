import pandas as pd
from .base_strategy import BaseStrategy
from trading_bot.utils import indicators

class OversoldReclaimStrategy(BaseStrategy):
    """
    Implements the 'Oversold Chart Pattern' entry strategy.

    This strategy looks for a potential reversal in an oversold stock.
    - BUY Signal: When a stock that is trading below its 200 SMA
      (in a long-term downtrend) "reclaims" the 8 EMA by crossing above it.
    - SELL Signal: This strategy does not define a SELL signal. Exits would be
      managed by a separate mechanism (e.g., profit target, stop loss, or another strategy).
    """
    def __init__(self):
        params = {"sma_period": 200, "ema_period": 8}
        super().__init__(name="Oversold Reclaim", params=params)

    def check_signal(self, ohlcv_data: pd.DataFrame) -> str:
        """
        Checks for a BUY signal based on the strategy rules.

        :param ohlcv_data: A pandas DataFrame with OHLCV data.
        :return: 'BUY' or 'HOLD'.
        """
        if len(ohlcv_data) < self.params["sma_period"]:
            return "HOLD" # Not enough data for the long-term SMA

        close_prices = ohlcv_data['Close']

        # Calculate indicators
        sma_200 = indicators.calculate_sma(close_prices, self.params["sma_period"])
        ema_8 = indicators.calculate_ema(close_prices, self.params["ema_period"])

        # Get the latest values
        latest_close = close_prices.iloc[-1]
        prev_close = close_prices.iloc[-2]
        latest_sma_200 = sma_200.iloc[-1]
        latest_ema_8 = ema_8.iloc[-1]
        prev_ema_8 = ema_8.iloc[-2]

        # --- Signal Logic ---

        # Condition 1: The stock is in a long-term downtrend (below SMA 200).
        is_in_downtrend = latest_close < latest_sma_200

        # Condition 2: The price just crossed above the 8 EMA.
        reclaimed_ema_8 = prev_close < prev_ema_8 and latest_close > latest_ema_8

        # BUY Signal: If both conditions are met, it's a potential reversal.
        if is_in_downtrend and reclaimed_ema_8:
            return "BUY"

        # This is primarily an entry strategy, so we only issue BUY or HOLD.
        return "HOLD"
