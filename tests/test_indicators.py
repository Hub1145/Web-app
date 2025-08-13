import unittest
import pandas as pd
import numpy as np
from trading_bot.utils.indicators import calculate_sma, calculate_ema, calculate_rsi

class TestIndicators(unittest.TestCase):
    """
    Tests for the technical indicator calculation functions.
    """

    @classmethod
    def setUpClass(cls):
        """Set up a sample DataFrame to be used across all tests."""
        cls.prices = pd.Series([10, 11, 12, 13, 14, 15, 16, 17, 18, 19])

    def test_calculate_sma(self):
        """
        Tests the Simple Moving Average (SMA) calculation.
        """
        sma_5 = calculate_sma(self.prices, 5)
        # The 5-period SMA of the last 5 prices (15, 16, 17, 18, 19) is 17.
        self.assertAlmostEqual(sma_5.iloc[-1], 17.0)
        # The 5-period SMA of the first 5 prices (10, 11, 12, 13, 14) is 12.
        self.assertAlmostEqual(sma_5.iloc[4], 12.0)
        # Check for NaN values at the beginning
        self.assertTrue(pd.isna(sma_5.iloc[3]))

    def test_calculate_ema(self):
        """
        Tests the Exponential Moving Average (EMA) calculation.
        The formula for EMA is more complex, so we test for general behavior
        and compare against pandas' own ewm function as a reference.
        """
        ema_5 = calculate_ema(self.prices, 5)
        # The EMA should be a valid number for all points after the first
        self.assertFalse(ema_5.isnull().any())
        # The EMA should be "pulled" towards the latest price.
        # For a rising series, EMA should be less than the last price but more than the first.
        self.assertGreater(ema_5.iloc[-1], self.prices.iloc[0])
        self.assertLess(ema_5.iloc[-1], self.prices.iloc[-1])

        # Compare with pandas ewm, which our function wraps. This is a sanity check.
        reference_ema = self.prices.ewm(span=5, adjust=False).mean()
        pd.testing.assert_series_equal(ema_5, reference_ema)

    def test_calculate_rsi(self):
        """
        Tests the Relative Strength Index (RSI) calculation.
        """
        # For a constantly rising series, RSI should be 100.
        rising_prices = pd.Series(range(10, 30))
        rsi_rising = calculate_rsi(rising_prices, 14)
        self.assertAlmostEqual(rsi_rising.iloc[-1], 100.0)

        # For a constantly falling series, RSI should be 0.
        falling_prices = pd.Series(range(30, 10, -1))
        rsi_falling = calculate_rsi(falling_prices, 14)
        self.assertAlmostEqual(rsi_falling.iloc[-1], 0.0)

        # Test with a mixed series
        mixed_prices = pd.Series([15, 16, 15, 17, 16, 18, 17, 19, 18, 20])
        rsi_mixed = calculate_rsi(mixed_prices, 4)
        # We expect a value between 0 and 100
        self.assertGreater(rsi_mixed.iloc[-1], 0)
        self.assertLess(rsi_mixed.iloc[-1], 100)


if __name__ == '__main__':
    unittest.main()
