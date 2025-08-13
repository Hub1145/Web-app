import pandas as pd
from .base_strategy import BaseStrategy
from trading_bot.utils import indicators

class DowntrendBreakStrategy(BaseStrategy):
    """
    Implements the 'Long-term Downtrend Break' strategy.

    - BUY Signal: When a stock that was in a downtrend (below SMA 200)
      reclaims the 8 EMA and then crosses above the 200 SMA.
    - SELL Signal: When a stock is trading below both the 200 SMA and 8 EMA.
    """
    def __init__(self):
        # Default parameters for this strategy
        params = {"sma_period": 200, "ema_period": 8}
        super().__init__(name="Long-term Downtrend Break", params=params)

    def check_signal(self, ohlcv_data: pd.DataFrame) -> str:
        """
        Checks for BUY, SELL, or HOLD signals based on the strategy rules.

        :param ohlcv_data: A pandas DataFrame with OHLCV data.
        :return: 'BUY', 'SELL', or 'HOLD'.
        """
        if len(ohlcv_data) < self.params["sma_period"]:
            return "HOLD" # Not enough data to calculate indicators

        close_prices = ohlcv_data['Close']

        # Calculate indicators
        sma_200 = indicators.calculate_sma(close_prices, self.params["sma_period"])
        ema_8 = indicators.calculate_ema(close_prices, self.params["ema_period"])

        # Get the latest values
        latest_close = close_prices.iloc[-1]
        prev_close = close_prices.iloc[-2]
        latest_sma_200 = sma_200.iloc[-1]
        prev_sma_200 = sma_200.iloc[-2]
        latest_ema_8 = ema_8.iloc[-1]

        # Handle case where there isn't enough data for a previous SMA value
        if pd.isna(prev_sma_200):
            return "HOLD"

        # --- Signal Logic ---

        # BUY Condition: Price crosses above the 200 SMA and is also above the 8 EMA.
        # This implies a recovery from a downtrend.
        buy_cross_above_sma200 = prev_close < prev_sma_200 and latest_close > latest_sma_200

        if buy_cross_above_sma200 and latest_close > latest_ema_8:
            return "BUY"

        # SELL Condition: Price is trading below both moving averages.
        # This indicates a confirmed downtrend.
        if latest_close < latest_sma_200 and latest_close < latest_ema_8:
            return "SELL"

        # HOLD Condition: All other cases.
        return "HOLD"
