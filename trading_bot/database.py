import sqlite3
import os

# Define the path for the database file within the trading_bot directory
DB_FILE = os.path.join(os.path.dirname(__file__), 'trading_bot.db')

def get_db_connection():
    """
    Creates a connection to the SQLite database.
    The connection object can be used as a context manager.
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row # Allows accessing columns by name
    return conn

def init_db():
    """
    Initializes the database by creating the necessary tables if they don't exist.
    This should be called once when the application starts.
    """
    print(f"Initializing database at {DB_FILE}...")
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # --- Bot Status Table (Key-Value Store) ---
        # Stores general status information about the bot.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bot_status (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # --- Portfolio Table ---
        # Stores the current open positions. This table should be cleared
        # and rewritten periodically to stay in sync with the broker.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolio (
                symbol TEXT PRIMARY KEY,
                quantity REAL NOT NULL,
                entry_price REAL NOT NULL,
                market_value REAL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # --- Trade Log Table ---
        # An append-only log of all executed trades.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trade_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                symbol TEXT NOT NULL,
                strategy TEXT NOT NULL,
                action TEXT NOT NULL, -- 'BUY' or 'SELL'
                quantity REAL NOT NULL,
                price REAL,
                status TEXT -- 'SUCCESS', 'FAILED'
            )
        """)

        conn.commit()
    print("Database initialized successfully.")

if __name__ == '__main__':
    # This allows running the script directly to initialize the database
    init_db()
    print("Database file 'trading_bot.db' created/updated.")
