import websocket
import json
import threading
import time
from trading_bot import config

class SECFeedClient:
    """
    A client to connect to a real-time SEC filings feed via WebSocket.
    This implementation simulates a connection for demonstration purposes.
    """
    def __init__(self):
        self.settings = config.SEC_API_SETTINGS
        self.url = self.settings.get("url")
        self.api_key = self.settings.get("api_key")
        self.ws = None
        self.thread = None

    def _on_message(self, ws, message):
        """
        Callback function to handle incoming SEC filing messages.
        """
        try:
            data = json.loads(message)
            print(f"[*] Received SEC Filing: Form {data.get('formType')} for {data.get('ticker')}")
            # In a real system, this would be put into a queue
            # for the trading logic to analyze for opportunities.
        except json.JSONDecodeError:
            print(f"[*] Received non-JSON message: {message}")

    def _on_error(self, ws, error):
        """Callback for WebSocket errors."""
        print(f"[!] SEC Feed Error: {error}")

    def _on_close(self, ws, close_status_code, close_msg):
        """Callback when the WebSocket connection is closed."""
        print("[*] SEC Feed connection closed.")

    def _on_open(self, ws):
        """
        Callback when the WebSocket connection is opened.
        """
        print("[*] SEC Feed connection opened.")
        # Example subscription message
        # sub_message = {"action": "subscribe", "key": self.api_key, "forms": ["4", "8-K"]}
        # ws.send(json.dumps(sub_message))

    def connect(self):
        """
        Establishes a connection to the WebSocket server.
        Runs in a separate thread to be non-blocking.
        """
        print(f"Attempting to connect to SEC Feed at {self.url}...")

        self.thread = threading.Thread(target=self._simulate_run)
        self.thread.daemon = True
        self.thread.start()

    def _simulate_run(self):
        """
        Simulates a running WebSocket client, periodically "receiving" messages.
        """
        self._on_open(None)
        mock_filings = [
            {"formType": "4", "ticker": "TSLA", "insiderName": "Elon Musk", "transaction": "Buy"},
            {"formType": "8-K", "ticker": "MSFT", "description": "Entry into a Material Definitive Agreement"},
            {"formType": "4", "ticker": "NVDA", "insiderName": "Jensen Huang", "transaction": "Sell"},
        ]

        try:
            while True:
                for filing in mock_filings:
                    self._on_message(None, json.dumps(filing))
                    time.sleep(25) # Simulate receiving filings every 25 seconds
        except KeyboardInterrupt:
            self._on_close(None, None, None)

    def stop(self):
        """Stops the WebSocket client thread."""
        if self.ws:
            self.ws.close()
        print("SEC Feed client stopped.")


if __name__ == '__main__':
    # Example of how to run the client
    sec_client = SECFeedClient()
    sec_client.connect()

    print("SEC client is running in the background. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        sec_client.stop()
        print("Program terminated.")
