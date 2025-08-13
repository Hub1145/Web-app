import websocket
import json
import threading
import time
from trading_bot import config

class NewsFeedClient:
    """
    A client to connect to a real-time news feed via WebSocket.
    """
    def __init__(self):
        self.settings = config.NEWS_API_SETTINGS
        self.url = self.settings.get("url")
        self.api_key = self.settings.get("api_key")
        self.ws_app = None
        self.thread = None

    def _on_message(self, ws, message):
        """
        Callback function to handle incoming messages.
        """
        try:
            data = json.loads(message)
            print(f"[*] Received News: {data.get('headline', 'No Headline')}")
            # In a real application, this data would be passed to a
            # thread-safe queue for the main logic to consume.
        except json.JSONDecodeError:
            print(f"[*] Received non-JSON message: {message}")

    def _on_error(self, ws, error):
        """Callback for WebSocket errors."""
        print(f"[!] News Feed Error: {error}")

    def _on_close(self, ws, close_status_code, close_msg):
        """Callback when the WebSocket connection is closed."""
        print("[*] News Feed connection closed.")
        # Optional: Implement reconnection logic here.
        time.sleep(5)
        print("[*] Reconnecting news feed...")
        self.connect()


    def _on_open(self, ws):
        """
        Callback when the WebSocket connection is opened.
        Sends an authentication or subscription message.
        """
        print("[*] News Feed connection opened.")
        # Most WebSocket APIs require an authentication or subscription message.
        # This is a generic example.
        auth_message = {
            "action": "auth",
            "key": self.api_key
        }
        try:
            ws.send(json.dumps(auth_message))
        except Exception as e:
            print(f"[!] Error sending auth message to news feed: {e}")

    def connect(self):
        """
        Establishes a persistent connection to the WebSocket server.
        """
        print(f"Connecting to News Feed at {self.url}...")
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
        print("News Feed client stopped.")


if __name__ == '__main__':
    # This is an example of how to run the client.
    # It will likely fail if the URL in config.py is a placeholder.
    news_client = NewsFeedClient()
    news_client.connect()

    print("News client is running. Press Ctrl+C to stop.")
    try:
        # Keep the main thread alive to see the output from the client thread.
        while news_client.thread and news_client.thread.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        news_client.stop()
        print("Program terminated.")
