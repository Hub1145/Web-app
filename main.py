import time
import pandas as pd

# --- Import all the components ---
from trading_bot import database
from trading_bot.brokers.tradestation_api import TradeStationAPI
from trading_bot.execution.trade_manager import TradeManager
from trading_bot.strategies.filters import apply_filters
from trading_bot.strategies.downtrend_break import DowntrendBreakStrategy
from trading_bot.strategies.oversold_reclaim import OversoldReclaimStrategy
from trading_bot.websocket.news_ws_server import NewsWSServer
from trading_bot.data.news_feed import MarketAuxNewsFetcher

def update_bot_status(key: str, value: str):
    """Helper function to update the bot's status in the database."""
    with database.get_db_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO bot_status (key, value) VALUES (?, ?)",
            (key, value)
        )
        conn.commit()

def main():
    """
    The main application loop for the trading bot.
    """
    print("--- Starting Trading Bot ---")

    # 1. Initialize database
    database.init_db()
    update_bot_status("engine_status", "Initializing")

    # 2. Initialize API and Trade Manager
    try:
        # Determine trading environment from database setting
        with database.get_db_connection() as conn:
            row = conn.execute("SELECT value FROM bot_status WHERE key = 'trading_mode'").fetchone()
            trading_mode = row['value'] if row else 'sim'

        print(f"[*] Initializing bot in '{trading_mode.upper()}' mode.")
        api_client = TradeStationAPI(environment=trading_mode)

        # Fetch the primary account key to use for trading
        accounts = api_client.get_user_accounts()
        if accounts and accounts.get("Accounts"):
            account_key = accounts["Accounts"][0]["AccountID"]
            trade_manager = TradeManager(api_client, account_key)
            print(f"Successfully connected. Trading on account {account_key}.")
        else:
            raise Exception("Could not retrieve account information from broker.")

    except Exception as e:
        print(f"[!] Critical error during initialization: {e}. Bot cannot start.")
        update_bot_status("engine_status", "Failed")
        return # Exit if we can't initialize a trade manager

    # 3. Instantiate all strategies you want to run
    strategies_to_run = [
        DowntrendBreakStrategy(),
        OversoldReclaimStrategy(),
    ]

    # The universe of symbols to consider
    symbol_universe = ["AAPL", "MSFT", "GOOG", "TSLA", "NVDA", "AMD", "PFE"]

    # 4. Initialize and start News Services
    news_ws_server = NewsWSServer()
    news_ws_server.start()
    time.sleep(1) # Give the server a moment to start

    news_fetcher = MarketAuxNewsFetcher(ws_server=news_ws_server, symbols=symbol_universe)
    news_fetcher.start()

    print("Bot initialized. Starting main loop...")

    # 5. Main application loop
    update_bot_status("engine_status", "Running")
    while True:
        try:
            print("\n" + "="*50)
            print(f"[{time.ctime()}] --- Running new trading cycle ---")
            update_bot_status("last_cycle_start", time.ctime())

            # a. Apply Filters
            filtered_symbols = apply_filters(symbol_universe, api_client)
            print(f"Filtered symbols to analyze: {filtered_symbols}")

            # b. Fetch Data and Check Strategies for each symbol
            for symbol in filtered_symbols:
                print(f"\n--- Analyzing {symbol} ---")

                raw_data = api_client.get_historical_bars(symbol)
                if not raw_data or "Bars" not in raw_data:
                    print(f"[!] Could not fetch historical data for {symbol}. Skipping.")
                    continue

                # Convert the bar data to a pandas DataFrame
                ohlcv_data = pd.DataFrame(raw_data["Bars"])
                ohlcv_data['TimeStamp'] = pd.to_datetime(ohlcv_data['TimeStamp'])
                ohlcv_data.set_index('TimeStamp', inplace=True)
                # Ensure correct column names if they differ
                ohlcv_data.rename(columns={'OpenBar': 'Open', 'HighBar': 'High', 'LowBar': 'Low', 'CloseBar': 'Close', 'TotalVolume': 'Volume'}, inplace=True)

                # c. Check against each strategy
                for strategy in strategies_to_run:
                    signal = strategy.check_signal(ohlcv_data)
                    print(f"Strategy '{strategy.name}' on {symbol}: -> {signal}")

                    if signal in ['BUY', 'SELL']:
                        # d. Execute trade if a signal is generated
                        trade_manager.execute_trade(symbol, signal, strategy.name)

            print("\n" + "="*50)
            print("Cycle complete. Waiting for next run...")
            update_bot_status("last_cycle_finish", time.ctime())
            # Wait for 5 minutes before the next cycle
            time.sleep(300)

        except KeyboardInterrupt:
            print("\nBot shutting down...")
            news_fetcher.stop()
            news_ws_server.stop()
            update_bot_status("engine_status", "Stopped")
            break
        except Exception as e:
            print(f"[!!!] An unexpected error occurred in the main loop: {e}")
            update_bot_status("engine_status", f"Error: {e}")
            print("Restarting cycle in 60 seconds...")
            time.sleep(60)

if __name__ == "__main__":
    main()
