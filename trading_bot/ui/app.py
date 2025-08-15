from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
import os

from trading_bot import config

# Create the Flask app
# The template_folder is set to be in the same directory as this script
app = Flask(__name__, template_folder='templates', static_folder='static')

# It's crucial to set a secret key for session management
# We'll try to get it from an environment variable, or use a default
# In a real app, this default key should NOT be used.
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "a-very-secret-key-for-dev")

# --- User Authentication ---

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == config.ADMIN_USERNAME and password == config.ADMIN_PASSWORD:
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# --- Main Application Routes ---

from trading_bot import database
from trading_bot.brokers.tradestation_api import TradeStationAPI

# --- Helper Functions ---
def get_status_from_db():
    """Fetches key-value status data from the database."""
    with database.get_db_connection() as conn:
        status_rows = conn.execute("SELECT key, value FROM bot_status").fetchall()
        return {row['key']: row['value'] for row in status_rows}

def get_portfolio_from_db():
    """Fetches the current portfolio from the database."""
    with database.get_db_connection() as conn:
        return conn.execute("SELECT * FROM portfolio ORDER BY symbol").fetchall()

@app.route('/')
@login_required
def dashboard():
    # Fetch live data from the database and API
    bot_status = get_status_from_db()
    portfolio = get_portfolio_from_db()

    # For live account balance, we need an API client
    # Note: In a real multi-user system, you'd manage clients better.
    account_summary = {"broker_name": "TradeStation", "balance": "N/A", "equity": "N/A", "pnl": 0}
    try:
        # Get trading mode from session, default to 'sim'
        trading_mode = session.get('trading_mode', 'sim')
        api_client = TradeStationAPI(environment=trading_mode)

        # Update the summary to show the current mode
        account_summary["broker_name"] = f"TradeStation ({trading_mode.upper()})"

        if api_client.api_key and "YOUR_API_KEY" not in api_client.api_key:
            accounts = api_client.get_user_accounts()
            if accounts and accounts.get("Accounts"):
                acc_key = accounts["Accounts"][0]["AccountID"]
                balances = api_client.get_account_balances(acc_key)
                if balances and balances.get("Balances"):
                    bal = balances["Balances"][0]
                    account_summary["balance"] = f"{float(bal.get('AccountCurrencyBalance', 0)):,.2f}"
                    account_summary["equity"] = f"{float(bal.get('Equity', 0)):,.2f}"
                    account_summary["pnl"] = float(bal.get('UnrealizedProfitLoss', 0))
    except Exception as e:
        print(f"[UI] Could not fetch live account balance: {e}")

    return render_template(
        'dashboard.html',
        username=session.get('username'),
        bot_status=bot_status,
        portfolio=portfolio,
        account_summary=account_summary
    )

@app.route('/brokers')
@login_required
def brokers():
    # Placeholder page
    return "<h1>Brokers Management Page (Placeholder)</h1>"

@app.route('/strategies')
@login_required
def strategies():
    # Placeholder page
    return "<h1>Strategies Management Page (Placeholder)</h1>"

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        trading_mode = request.form.get('trading_mode')
        if trading_mode in ['sim', 'live']:
            # Store in the database for the bot process
            with database.get_db_connection() as conn:
                conn.execute("INSERT OR REPLACE INTO bot_status (key, value) VALUES (?, ?)", ("trading_mode", trading_mode))
                conn.commit()
            # Also store in session for the UI
            session['trading_mode'] = trading_mode
            flash(f'Trading mode set to {trading_mode.upper()}. Bot will use this setting on its next cycle/restart.', 'success')
        else:
            flash('Invalid trading mode selected.', 'error')
        return redirect(url_for('settings'))

    # Read from DB to show the authoritative current setting
    with database.get_db_connection() as conn:
        row = conn.execute("SELECT value FROM bot_status WHERE key = 'trading_mode'").fetchone()
        current_mode = row['value'] if row else 'sim'
        session['trading_mode'] = current_mode # Sync session with DB on page load

    return render_template('settings.html', current_mode=current_mode)

@app.route('/log')
@login_required
def trade_log():
    """Displays the history of all trades from the database."""
    with database.get_db_connection() as conn:
        log_entries = conn.execute("SELECT * FROM trade_log ORDER BY timestamp DESC").fetchall()
    return render_template('trade_log.html', trade_log=log_entries)

if __name__ == '__main__':
    # Running in debug mode is convenient for development but should be
    # disabled in a production environment.
    app.run(debug=True, port=5001)
