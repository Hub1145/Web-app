from trading_bot.brokers.tradestation_api import TradeStationAPI
from trading_bot import database

class TradeManager:
    """
    Manages trade execution and position tracking by writing to the database.
    """
    def __init__(self, api_client: TradeStationAPI, account_key: str):
        """
        Initializes the TradeManager with a broker API client and a specific account key.

        :param api_client: An instance of a broker API client (e.g., TradeStationAPI).
        :param account_key: The specific account ID to trade on.
        """
        self.api_client = api_client
        self.account_key = account_key
        # Ensure the portfolio is up-to-date on startup
        self._update_portfolio_db()

    def _get_open_positions(self) -> dict:
        """
        Fetches and returns a dictionary of open positions from the broker.
        :return: A dictionary mapping symbols to their position data, or an empty dict.
        """
        if not self.api_client:
            print("[TradeManager] No API client, cannot fetch positions.")
            return {}

        positions_data = self.api_client.get_positions(self.account_key)
        if positions_data and "Positions" in positions_data:
            return {pos['Symbol']: pos for pos in positions_data["Positions"]}
        return {}

    def _update_portfolio_db(self):
        """
        Fetches the latest portfolio from the broker and updates the database.
        """
        print("[TradeManager] Syncing portfolio with database...")
        positions = self._get_open_positions()

        with database.get_db_connection() as conn:
            cursor = conn.cursor()
            # Clear the table to ensure it's always in sync
            cursor.execute("DELETE FROM portfolio")

            if not positions:
                print("[TradeManager] No open positions found.")
                conn.commit()
                return

            for symbol, pos_data in positions.items():
                cursor.execute(
                    """
                    INSERT INTO portfolio (symbol, quantity, entry_price, market_value)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        pos_data.get("Symbol"),
                        pos_data.get("Quantity"),
                        pos_data.get("AveragePrice"),
                        pos_data.get("MarketValue")
                    ),
                )
            conn.commit()
        print(f"[TradeManager] Portfolio sync complete. {len(positions)} positions updated.")

    def _log_trade_db(self, symbol, strategy, action, quantity, price, status):
        """Logs a trade event to the database."""
        with database.get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO trade_log (symbol, strategy, action, quantity, price, status)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (symbol, strategy, action, quantity, price, status),
            )
            conn.commit()

    def execute_trade(self, symbol: str, signal: str, strategy_name: str):
        """
        Analyzes a signal, places a real order, and logs the result.
        """
        if not self.api_client:
            print(f"[TradeManager] SIMULATING {signal} for {symbol} due to no API client.")
            return

        open_positions = self._get_open_positions()
        price = None
        status = "FAILED"
        quantity = 0

        try:
            if signal == 'BUY':
                if symbol in open_positions:
                    print(f"[TradeManager] IGNORE BUY: Position already exists for {symbol}.")
                    return

                print(f"[TradeManager] EXECUTING LIVE BUY for {symbol} based on '{strategy_name}'.")
                quantity = 10  # Fixed quantity for simplicity
                order_result = self.api_client.place_order(self.account_key, symbol, quantity, "Market", "BUY")

                if order_result and order_result.get("Orders"):
                    price = order_result["Orders"][0].get("Fills")[0].get("FillPrice")
                    status = "SUCCESS"
                    print(f"[TradeManager] BUY order successful: {order_result}")
                else:
                    print(f"[TradeManager] BUY order failed or returned no result.")

            elif signal == 'SELL':
                if symbol not in open_positions:
                    print(f"[TradeManager] IGNORE SELL: No position exists for {symbol}.")
                    return

                print(f"[TradeManager] EXECUTING LIVE SELL for {symbol} based on '{strategy_name}'.")
                quantity = open_positions[symbol].get("Quantity")
                order_result = self.api_client.place_order(self.account_key, symbol, quantity, "Market", "SELL")

                if order_result and order_result.get("Orders"):
                    price = order_result["Orders"][0].get("Fills")[0].get("FillPrice")
                    status = "SUCCESS"
                    print(f"[TradeManager] SELL order successful: {order_result}")
                else:
                    print(f"[TradeManager] SELL order failed or returned no result.")

        except Exception as e:
            print(f"[TradeManager] Exception during {signal} order for {symbol}: {e}")
            status = "FAILED"

        finally:
            # Log every attempt, successful or not
            if signal in ['BUY', 'SELL']:
                self._log_trade_db(symbol, strategy_name, signal, quantity, price, status)

            # Always update the portfolio after any trade action
            self._update_portfolio_db()
