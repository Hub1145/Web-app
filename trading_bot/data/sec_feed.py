import websocket
import json
import threading
import time
from trading_bot import config

class SECFeedClient:
    """
    A client to connect to a real-time SEC filings feed via WebSocket.
    """
    def __init__(self):
        self.settings = config.SEC_API_SETTINGS
        self.url = self.settings.get("url")
        self.api_key = self.settings.get("api_key")
        self.ws_app = None
        self.thread = None

    def _on_message(self, ws, message):
        """
        Callback function to handle incoming SEC filing messages.
        """
        try:
            data = json.loads(message)
            print(f"[*] Received SEC Filing: Form {data.get('formType')} for {data.get('ticker')}")
            # In a real system, this would be put into a queue
            # for the trading logic to analyze.
        except json.JSONDecodeError:
            print(f"[*] Received non-JSON message: {message}")

    def _on_error(self, ws, error):
        """Callback for WebSocket errors."""
        print(f"[!] SEC Feed Error: {error}")

    def _on_close(self, ws, close_status_code, close_msg):
        """Callback when the WebSocket connection is closed."""
        print("[*] SEC Feed connection closed.")
        # Optional: Implement reconnection logic here.
        time.sleep(5)
        print("[*] Reconnecting SEC feed...")
        self.connect()

    def _on_open(self, ws):
        """
        Callback when the WebSocket connection is opened.
        Sends a subscription message.
        """
        print("[*] SEC Feed connection opened.")
        # Example subscription message for specific form types
        sub_message = {
            "action": "subscribe",
            "key": self.api_key,
            "forms": ["4", "8-K"]
        }
        try:
            ws.send(json.dumps(sub_message))
        except Exception as e:
            print(f"[!] Error sending subscription message to SEC feed: {e}")

    def connect(self):
        """
        Establishes a persistent connection to the WebSocket server.
        """
        print(f"Connecting to SEC Feed at {self.url}...")
        self.ws_app = websocket.WebSocketApp(
            self.url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )

        # Run the WebSocket client in a separate thread
        self.thread = threading.Thread(target=self.ws_app.run_forever)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        """Stops the WebSocket client thread."""
        if self.ws_app:
            self.ws_app.close()
        print("SEC Feed client stopped.")


if __name__ == '__main__':
    # This is an example of how to run the client.
    # It will likely fail if the URL in config.py is a placeholder.
    sec_client = SECFeedClient()
    sec_client.connect()

    print("SEC client is running. Press Ctrl+C to stop.")
    try:
        while sec_client.thread and sec_client.thread.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        sec_client.stop()
        print("Program terminated.")
