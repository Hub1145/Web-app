import pandas as pd

def calculate_sma(data: pd.Series, period: int) -> pd.Series:
    """
    Calculates the Simple Moving Average (SMA).

    :param data: A pandas Series (e.g., closing prices).
    :param period: The moving average period.
    :return: A pandas Series with the SMA values.
    """
    if not isinstance(data, pd.Series):
        raise TypeError("data must be a pandas Series.")
    if period > len(data):
        return pd.Series(index=data.index) # Return empty series if not enough data
    return data.rolling(window=period).mean()

def calculate_ema(data: pd.Series, period: int) -> pd.Series:
    """
    Calculates the Exponential Moving Average (EMA).

    :param data: A pandas Series (e.g., closing prices).
    :param period: The moving average period.
    :return: A pandas Series with the EMA values.
    """
    if not isinstance(data, pd.Series):
        raise TypeError("data must be a pandas Series.")
    return data.ewm(span=period, adjust=False).mean()

def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculates the Relative Strength Index (RSI).

    :param data: A pandas Series (e.g., closing prices).
    :param period: The RSI period.
    :return: A pandas Series with the RSI values.
    """
    if not isinstance(data, pd.Series):
        raise TypeError("data must be a pandas Series.")
    if period > len(data):
        return pd.Series(index=data.index)

    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi
