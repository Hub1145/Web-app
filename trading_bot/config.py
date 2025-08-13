import os

# --- Security Configuration ---
# This key is used for encrypting and decrypting sensitive data like API keys.
# In a production environment, this should be loaded securely, for example from
# an environment variable or a secret management service.
# You can generate a new key by running:
# from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())
SECRET_KEY = os.environ.get("SECRET_KEY", "your-super-secret-fernet-key-goes-here")


# --- Broker Configuration (TradeStation) ---
# It is strongly recommended to use environment variables for these settings.
# The application will look for these environment variables first, and fall back
# to the hardcoded values below if they are not found. The hardcoded values
# are placeholders and should be replaced by the user.

TRADESTATION_SETTINGS = {
    "api_key": os.environ.get("TS_API_KEY", "YOUR_API_KEY"),
    "api_secret": os.environ.get("TS_API_SECRET", "YOUR_API_SECRET"),
    "username": os.environ.get("TS_USERNAME", "YOUR_USERNAME"),
    "password": os.environ.get("TS_PASSWORD", "YOUR_PASSWORD"),
    # Set to 'live' for real trading or 'sim' for paper trading.
    "environment": os.environ.get("TS_ENVIRONMENT", "sim"),
}

# --- API Endpoints ---
TRADESTATION_URLS = {
    "live": "https://api.tradestation.com/v3",
    "sim": "https://sim-api.tradestation.com/v3",
    "auth": "https://signin.tradestation.com/oauth/token",
}

# --- News API Configuration ---
# Using placeholders for a generic news streaming service
NEWS_API_SETTINGS = {
    "api_key": os.environ.get("NEWS_API_KEY", "YOUR_NEWS_API_KEY"),
    "url": os.environ.get("NEWS_API_URL", "wss://your-news-api-websocket-url"),
}

# --- SEC Filings API Configuration ---
# Using placeholders for a generic SEC filings streaming service
SEC_API_SETTINGS = {
    "api_key": os.environ.get("SEC_API_KEY", "YOUR_SEC_API_KEY"),
    "url": os.environ.get("SEC_API_URL", "wss://your-sec-api-websocket-url"),
}
