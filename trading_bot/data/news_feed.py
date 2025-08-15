import requests
import json
import threading
import time
import asyncio
from trading_bot import config
from trading_bot.websocket.news_ws_server import NewsWSServer

class MarketAuxNewsFetcher:
    """
    Fetches news from the MarketAux REST API and broadcasts it via a WebSocket server.
    """
    def __init__(self, ws_server: NewsWSServer, symbols: list):
        self.settings = config.NEWS_API_SETTINGS
        self.url = self.settings.get("url")
        self.api_key = self.settings.get("api_key")
        self.ws_server = ws_server
        self.symbols = symbols
        self.thread = None
        self._stop_event = threading.Event()

    def _fetch_and_broadcast(self):
        """
        The main loop that runs in a thread to fetch and broadcast news.
        """
        while not self._stop_event.is_set():
            print("[*] Fetching news from MarketAux...")
            try:
                params = {
                    "api_token": self.api_key,
                    "symbols": ",".join(self.symbols),
                    "language": "en",
                }
                response = requests.get(self.url, params=params)
                response.raise_for_status()  # Raise an exception for bad status codes

                news_data = response.json()

                if "data" in news_data:
                    for article in news_data["data"]:
                        # Prepare a message to broadcast
                        message = json.dumps({
                            "headline": article.get("title"),
                            "source": article.get("source"),
                            "url": article.get("url"),
                            "summary": article.get("snippet"),
                            "timestamp": article.get("published_at"),
                        })

                        # Use asyncio.run_coroutine_threadsafe to call the async broadcast method
                        # from this synchronous thread.
                        if self.ws_server.loop:
                            future = asyncio.run_coroutine_threadsafe(self.ws_server.broadcast(message), self.ws_server.loop)
                            future.result(timeout=2) # Wait for the broadcast to complete

                        print(f"[*] Broadcasted news: {article.get('title')}")

            except requests.exceptions.RequestException as e:
                print(f"[!] Error fetching news from MarketAux: {e}")
            except Exception as e:
                print(f"[!] An unexpected error occurred in the news fetcher: {e}")

            # Wait for 60 seconds before the next fetch.
            # MarketAux free plan has limits, so we don't want to poll too frequently.
            time.sleep(60)

    def start(self):
        """Starts the news fetcher in a separate daemon thread."""
        if self.thread is None or not self.thread.is_alive():
            self._stop_event.clear()
            self.thread = threading.Thread(target=self._fetch_and_broadcast)
            self.thread.daemon = True
            self.thread.start()
            print("[*] MarketAux News Fetcher thread started.")

    def stop(self):
        """Stops the news fetcher thread."""
        if self.thread and self.thread.is_alive():
            self._stop_event.set()
            self.thread.join(timeout=5)
            print("[*] MarketAux News Fetcher stopped.")
        self.thread = None

# Example of how to run the fetcher
if __name__ == '__main__':
    # 1. Start the WebSocket server
    news_server = NewsWSServer()
    news_server.start()

    # Give the server a moment to start up
    time.sleep(2)

    # 2. Start the news fetcher
    # For the example, we use a predefined list of symbols
    example_symbols = ["AAPL", "TSLA"]
    news_fetcher = MarketAuxNewsFetcher(ws_server=news_server, symbols=example_symbols)
    news_fetcher.start()

    print("News fetcher is running. Press Ctrl+C to stop.")
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        news_fetcher.stop()
        news_server.stop()
        print("\nProgram terminated.")
