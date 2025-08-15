import requests
import time
from datetime import datetime, timedelta

from trading_bot import config

class TradeStationAPI:
    """
    A wrapper for the TradeStation API.
    Handles authentication, token refreshing, and API requests.
    """
    def __init__(self, environment="sim"):
        self.settings = config.TRADESTATION_SETTINGS
        self.urls = config.TRADESTATION_URLS

        self.environment = environment
        self.base_url = self.urls.get(self.environment)

        if not self.base_url:
            raise ValueError(f"Invalid environment specified: {self.environment}")

        self.api_key = self.settings.get("api_key")
        self.api_secret = self.settings.get("api_secret")
        self.username = self.settings.get("username")
        self.password = self.settings.get("password")

        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None

    def _authenticate(self):
        """
        Performs initial authentication to get an access and refresh token.
        """
        auth_url = self.urls["auth"]
        payload = {
            "grant_type": "password",
            "client_id": self.api_key,
            "client_secret": self.api_secret,
            "username": self.username,
            "password": self.password,
            "response_type": "token",
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        try:
            response = requests.post(auth_url, headers=headers, data=payload)
            response.raise_for_status()
            data = response.json()

            self.access_token = data["access_token"]
            self.refresh_token = data["refresh_token"]
            # Set expiration time with a small buffer (e.g., 60 seconds)
            expires_in = int(data["expires_in"]) - 60
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)

            print("Successfully authenticated with TradeStation.")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error authenticating with TradeStation: {e}")
            print(f"Response: {e.response.text if e.response else 'No response'}")
            return False

    def _refresh_access_token(self):
        """
        Refreshes the access token using the refresh token.
        """
        auth_url = self.urls["auth"]
        payload = {
            "grant_type": "refresh_token",
            "client_id": self.api_key,
            "client_secret": self.api_secret,
            "refresh_token": self.refresh_token,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        try:
            response = requests.post(auth_url, headers=headers, data=payload)
            response.raise_for_status()
            data = response.json()

            self.access_token = data["access_token"]
            # Some OAuth flows provide a new refresh token
            self.refresh_token = data.get("refresh_token", self.refresh_token)
            expires_in = int(data["expires_in"]) - 60
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)

            print("Successfully refreshed access token.")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error refreshing access token: {e}")
            return False

    def _ensure_token_valid(self):
        """
        Ensures the access token is valid, authenticating or refreshing if necessary.
        """
        if not self.access_token:
            return self._authenticate()

        if datetime.now() >= self.token_expires_at:
            return self._refresh_access_token()

        return True

    def _make_request(self, method, endpoint, params=None, json_data=None):
        """
        A centralized method for making authenticated API requests.
        """
        if not self._ensure_token_valid():
            raise Exception("Failed to obtain a valid API token.")

        url = f"{self.base_url}{endpoint}"
        headers = {"Authorization": f"Bearer {self.access_token}"}

        try:
            response = requests.request(method, url, headers=headers, params=params, json=json_data)
            response.raise_for_status()
            # Some successful responses might not have a JSON body (e.g., 204 No Content)
            if response.status_code == 204:
                return None
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            print(f"Response: {e.response.text if e.response else 'No response'}")
            return None

    # --- Public API Methods ---

    def get_user_accounts(self):
        """
        Retrieves a list of accounts for the authenticated user.
        """
        return self._make_request("GET", "/brokerage/accounts")

    def get_account_balances(self, account_key):
        """
        Retrieves the balances for a specific account.
        """
        return self._make_request("GET", f"/brokerage/accounts/{account_key}/balances")

    def get_positions(self, account_key):
        """
        Retrieves the positions for a specific account.
        """
        return self._make_request("GET", f"/brokerage/accounts/{account_key}/positions")

    def get_quote(self, symbols):
        """
        Retrieves quotes for a list of symbols.
        """
        if isinstance(symbols, list):
            symbols = ",".join(symbols)
        return self._make_request("GET", f"/marketdata/quotes/{symbols}")

    def get_historical_bars(self, symbol, interval="Daily", unit="Days", bars_back=252):
        """
        Retrieves historical OHLCV bars for a symbol.

        :param symbol: The stock symbol (e.g., 'AAPL').
        :param interval: The interval of each bar (e.g., 'Daily', 'Minutes').
        :param unit: The unit for the interval (e.g., 'Days', 'Minutes').
        :param bars_back: The number of bars to fetch.
        :return: A dictionary containing the historical bar data.
        """
        params = {
            "symbol": symbol,
            "interval": bars_back,
            "unit": unit,
            "timeframe": interval
        }
        # Note: The TradeStation API documentation should be consulted for the exact
        # parameter names and values. This is a common structure.
        # The endpoint might be slightly different, e.g., /marketdata/barcharts/{symbol}
        return self._make_request("GET", f"/marketdata/barcharts/{symbol}", params=params)

    def place_order(self, account_key, symbol, quantity, order_type, trade_action):
        """
        Places a trade order.

        :param account_key: The account to place the order in.
        :param symbol: The stock symbol.
        :param quantity: The number of shares.
        :param order_type: 'Market', 'Limit', 'Stop', etc.
        :param trade_action: 'BUY' or 'SELL'.
        :return: A dictionary containing the order confirmation details.
        """
        endpoint = f"/brokerage/accounts/{account_key}/orders"

        # This is a representative payload. The actual required fields may vary
        # based on the TradeStation API documentation for different order types.
        order_payload = {
            "AccountID": account_key,
            "Symbol": symbol,
            "Quantity": str(quantity),
            "OrderType": order_type,
            "TradeAction": trade_action,
            "TimeInForce": {"Duration": "DAY"},
            "Route": "Intelligent",
        }

        return self._make_request("POST", endpoint, json_data=[order_payload])
