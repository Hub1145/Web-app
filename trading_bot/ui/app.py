from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
import os

# Create the Flask app
# The template_folder is set to be in the same directory as this script
app = Flask(__name__, template_folder='templates', static_folder='static')

# It's crucial to set a secret key for session management
# We'll try to get it from an environment variable, or use a default
# In a real app, this default key should NOT be used.
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "a-very-secret-key-for-dev")

# --- User Authentication (Placeholder) ---
# In a real application, this would be a database lookup.
DUMMY_USERS = {"admin": "password123"}

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
        if DUMMY_USERS.get(username) == password:
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

@app.route('/')
@login_required
def dashboard():
    # Mock data to populate the dashboard
    mock_account_summary = {
        "broker_name": "TradeStation (SIM)",
        "balance": "100,000.00",
        "equity": "105,250.50",
        "pnl": 5250.50
    }
    mock_bot_status = {
        "engine_status": "Running",
        "data_feeds_status": "Connected",
        "last_activity": "2 minutes ago"
    }
    mock_active_strategies = [
        {"name": "Long-term Downtrend Break", "symbols_count": 5, "status": "Active"},
        {"name": "Oversold Reclaim", "symbols_count": 3, "status": "Active"},
    ]
    return render_template(
        'dashboard.html',
        username=session.get('username'),
        account_summary=mock_account_summary,
        bot_status=mock_bot_status,
        active_strategies=mock_active_strategies
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

@app.route('/settings')
@login_required
def settings():
    # Placeholder page
    return "<h1>Settings Page (Placeholder)</h1>"

if __name__ == '__main__':
    # Running in debug mode is convenient for development but should be
    # disabled in a production environment.
    app.run(debug=True, port=5001)
