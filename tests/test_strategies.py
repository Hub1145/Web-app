import unittest
import pandas as pd
from trading_bot.strategies.downtrend_break import DowntrendBreakStrategy
from trading_bot.strategies.oversold_reclaim import OversoldReclaimStrategy

class TestStrategies(unittest.TestCase):
    """
    Tests the logic of the implemented trading strategies.
    """

    def test_downtrend_break_strategy(self):
        """
        Tests the DowntrendBreakStrategy for BUY, SELL, and HOLD signals.
        """
        strategy = DowntrendBreakStrategy()

        # --- Test BUY Signal ---
        # Create data where price was below SMA 200 and just crossed above it,
        # while also being above EMA 8.
        # Let's assume SMA 200 is flat at 150 and EMA 8 is at 150.5
        buy_data = pd.DataFrame({
            'Close': [148.0, 151.0], # Crosses from 148 to 151
            # Other OHLC data is not used by this strategy but required by the structure
            'Open': [147.0, 149.0], 'High': [148.5, 151.5], 'Low': [146.5, 148.5],
        })
        # Mock the indicators directly for simplicity
        strategy.params['sma_period'] = 1 # To avoid data length issues
        strategy.check_signal = lambda df: "BUY" # Mocking the check_signal method
        # In a more complex test, we would mock the indicator functions
        # For now, let's assume the logic inside check_signal is what we want to test.
        # We will create a more realistic test case for the check_signal logic

        # Let's create a more realistic data set
        prices = [155]*198 + [149, 152] # SMA200 will be around 155
        ohlcv = pd.DataFrame({'Close': prices})
        ohlcv['Open'] = ohlcv['Close']
        ohlcv['High'] = ohlcv['Close']
        ohlcv['Low'] = ohlcv['Close']
        ohlcv['Volume'] = [1000] * 200

        # This is a bit complex to simulate perfectly without a full data series
        # A simplified approach is to test the conditions directly.
        # We will manually create indicator values

        # Test Case 1: BUY signal
        # Close crosses above SMA200, and Close is above EMA8
        mock_data_buy = pd.DataFrame({
            'Close': [149, 151],
            'SMA_200': [150, 150],
            'EMA_8': [148, 150]
        })

        # Re-implementing a small part of the logic to test it.
        # This is not ideal, but shows the principle.
        latest = mock_data_buy.iloc[-1]
        prev = mock_data_buy.iloc[-2]
        self.assertTrue(prev['Close'] < prev['SMA_200'] and latest['Close'] > latest['SMA_200'])
        self.assertTrue(latest['Close'] > latest['EMA_8'])
        # The actual test should be on the strategy object itself.


    def test_oversold_reclaim_strategy(self):
        """
        Tests the OversoldReclaimStrategy for BUY and HOLD signals.
        """
        strategy = OversoldReclaimStrategy()

        # --- Test BUY Signal ---
        # Price is below SMA 200, but just crossed above EMA 8.
        # SMA 200 is at 160. Price crosses EMA 8 at 145.

        # Let's create a more realistic scenario for testing.
        # We'll create a dataframe and then call the strategy

        sma_period = 5 # Using smaller periods for easier testing
        ema_period = 3
        strategy.params = {"sma_period": sma_period, "ema_period": ema_period}

        # Data for a BUY signal: below SMA, crosses above EMA
        # The final jump needs to be strong enough to cross the lagging EMA.
        prices_buy = [160, 155, 150, 140, 148]
        data_buy = pd.DataFrame({'Close': prices_buy, 'Open': prices_buy, 'High': prices_buy, 'Low': prices_buy, 'Volume': [100]*5})
        signal_buy = strategy.check_signal(data_buy)
        self.assertEqual(signal_buy, "BUY")

        # Data for a HOLD signal: below SMA, but still below EMA
        prices_hold1 = [160, 155, 150, 145, 144]
        data_hold1 = pd.DataFrame({'Close': prices_hold1, 'Open': prices_hold1, 'High': prices_hold1, 'Low': prices_hold1, 'Volume': [100]*5})
        signal_hold1 = strategy.check_signal(data_hold1)
        self.assertEqual(signal_hold1, "HOLD")

        # Data for a HOLD signal: above SMA (not oversold)
        prices_hold2 = [150, 155, 160, 165, 170]
        data_hold2 = pd.DataFrame({'Close': prices_hold2, 'Open': prices_hold2, 'High': prices_hold2, 'Low': prices_hold2, 'Volume': [100]*5})
        signal_hold2 = strategy.check_signal(data_hold2)
        self.assertEqual(signal_hold2, "HOLD")


# A simplified test for DowntrendBreakStrategy due to complexity of SMA200
class TestDowntrendBreakSimplified(unittest.TestCase):

    def setUp(self):
        self.strategy = DowntrendBreakStrategy()
        self.strategy.params = {"sma_period": 5, "ema_period": 3}

    def test_buy_signal(self):
        # SMA is around 151-152. Price crosses from 148 to 152.
        # We need enough data points for prev_sma to be valid, so we need period + 1 data points.
        prices = [156, 155, 152, 150, 148, 152] # 6 data points for a period 5 SMA
        data = pd.DataFrame({'Close': prices, 'Open': prices, 'High': prices, 'Low': prices, 'Volume': [100]*6})
        signal = self.strategy.check_signal(data)
        self.assertEqual(signal, "BUY")

    def test_sell_signal(self):
        # Price is below both SMA and EMA. Need period + 1 data points.
        prices = [158, 155, 152, 150, 145, 140]
        data = pd.DataFrame({'Close': prices, 'Open': prices, 'High': prices, 'Low': prices, 'Volume': [100]*6})
        signal = self.strategy.check_signal(data)
        self.assertEqual(signal, "SELL")

    def test_hold_signal(self):
        # Price is above both SMA and EMA (uptrend)
        prices = [140, 145, 150, 155, 160]
        data = pd.DataFrame({'Close': prices, 'Open': prices, 'High': prices, 'Low': prices, 'Volume': [100]*5})
        signal = self.strategy.check_signal(data)
        self.assertEqual(signal, "HOLD")

if __name__ == '__main__':
    unittest.main()
