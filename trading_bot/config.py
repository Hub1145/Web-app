import json
import os

# --- Load Configuration from config.json ---

CONFIG_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')

# Default empty values
SECRET_KEY = None
TRADESTATION_SETTINGS = {}
NEWS_API_SETTINGS = {}
SEC_API_SETTINGS = {}
TRADESTATION_URLS = {
    "live": "https://api.tradestation.com/v3",
    "sim": "https://sim-api.tradestation.com/v3",
    "auth": "https://signin.tradestation.com/oauth/token",
}

try:
    with open(CONFIG_FILE_PATH, 'r') as f:
        config_data = json.load(f)

    SECRET_KEY = config_data.get("FERNET_SECRET_KEY")
    TRADESTATION_SETTINGS = config_data.get("TRADESTATION", {})
    NEWS_API_SETTINGS = config_data.get("NEWS_API", {})
    SEC_API_SETTINGS = config_data.get("SEC_API", {})

except FileNotFoundError:
    print(f"[!] CONFIGURATION ERROR: `config.json` not found at {CONFIG_FILE_PATH}.")
    print("[!] Please copy `config.json.example` to `config.json` and fill in your credentials.")
    # Exiting here is an option in a real app to prevent running with no config
    # import sys
    # sys.exit(1)
except json.JSONDecodeError:
    print(f"[!] CONFIGURATION ERROR: `config.json` is not a valid JSON file.")
except Exception as e:
    print(f"[!] An unexpected error occurred while reading the configuration: {e}")

# --- Legacy URL mapping (still useful) ---
# This part doesn't need to be in the JSON file as it's not a secret.
TRADESTATION_URLS = {
    "live": "https://api.tradestation.com/v3",
    "sim": "https://sim-api.tradestation.com/v3",
    "auth": "https://signin.tradestation.com/oauth/token",
}
