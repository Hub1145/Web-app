import time
import pandas as pd

# --- Import all the components ---
from trading_bot.brokers.tradestation_api import TradeStationAPI
from trading_bot.execution.trade_manager import TradeManager
from trading_bot.strategies.filters import apply_filters
from trading_bot.strategies.downtrend_break import DowntrendBreakStrategy
from trading_bot.strategies.oversold_reclaim import OversoldReclaimStrategy

def main():
    """
    The main application loop for the trading bot.
    """
    print("--- Starting Trading Bot ---")

    # 1. Initialize all components
    # NOTE: For this to run, the user must provide valid credentials in config.py
    # or as environment variables.
    try:
        api_client = TradeStationAPI()
        # A quick check to see if authentication would work at a high level
        if not api_client.api_key or "YOUR_API_KEY" in api_client.api_key:
             print("[!] WARNING: TradeStation API credentials are not set. The bot will run in full simulation mode.")
             api_client = None # Set to None to ensure we use mock data
    except Exception as e:
        print(f"[!] Could not initialize TradeStationAPI: {e}. Running in full simulation mode.")
        api_client = None

    trade_manager = TradeManager(api_client)

    # Instantiate all strategies you want to run
    strategies_to_run = [
        DowntrendBreakStrategy(),
        OversoldReclaimStrategy(),
    ]

    # The universe of symbols to consider
    symbol_universe = ["AAPL", "MSFT", "GOOG", "TSLA", "NVDA", "AMD", "PFE"]

    print("Bot initialized. Starting main loop...")

    # 2. Main application loop
    while True:
        try:
            print("\n" + "="*50)
            print(f"[{time.ctime()}] --- Running new trading cycle ---")

            # 3. Apply Filters
            if api_client:
                # In a live environment, this would call the real API
                filtered_symbols = apply_filters(symbol_universe, api_client)
            else:
                # In simulation mode, we just use a subset of the universe
                print("[SIM] Skipping real-time filtering.")
                filtered_symbols = ["AAPL", "MSFT", "TSLA"]

            print(f"Filtered symbols to analyze: {filtered_symbols}")

            # 4. Fetch Data and Check Strategies for each symbol
            for symbol in filtered_symbols:
                print(f"\n--- Analyzing {symbol} ---")

                # a. Fetch historical data
                ohlcv_data = None
                if api_client:
                    # This would be a real API call
                    raw_data = api_client.get_historical_bars(symbol)
                    if raw_data and "Bars" in raw_data:
                         # Convert the bar data to a pandas DataFrame
                         df = pd.DataFrame(raw_data["Bars"])
                         df['TimeStamp'] = pd.to_datetime(df['TimeStamp'])
                         df.set_index('TimeStamp', inplace=True)
                         # Ensure correct column names if they differ
                         df.rename(columns={'OpenBar': 'Open', 'HighBar': 'High', 'LowBar': 'Low', 'CloseBar': 'Close', 'TotalVolume': 'Volume'}, inplace=True)
                         ohlcv_data = df

                if ohlcv_data is None:
                    # Provide mock data if the API call fails or is simulated
                    print(f"[SIM] Using mock OHLCV data for {symbol}.")
                    mock_dates = pd.date_range(end=pd.Timestamp.now(), periods=252)
                    ohlcv_data = pd.DataFrame({
                        'Open': [150 + i * 0.1 for i in range(252)],
                        'High': [152 + i * 0.1 for i in range(252)],
                        'Low': [148 + i * 0.1 for i in range(252)],
                        'Close': [151 + i * 0.1 for i in range(252)],
                        'Volume': [1000000 + i * 1000 for i in range(252)],
                    }, index=mock_dates)

                # b. Check against each strategy
                for strategy in strategies_to_run:
                    signal = strategy.check_signal(ohlcv_data)
                    print(f"Strategy '{strategy.name}' on {symbol}: -> {signal}")

                    if signal in ['BUY', 'SELL']:
                        # c. Execute trade if a signal is generated
                        trade_manager.execute_trade(symbol, signal, strategy.name)

            print("\n" + "="*50)
            print("Cycle complete. Waiting for next run...")
            # Wait for 5 minutes before the next cycle
            time.sleep(300)

        except KeyboardInterrupt:
            print("\nBot shutting down...")
            break
        except Exception as e:
            print(f"[!!!] An unexpected error occurred in the main loop: {e}")
            print("Restarting cycle in 60 seconds...")
            time.sleep(60)

if __name__ == "__main__":
    main()
