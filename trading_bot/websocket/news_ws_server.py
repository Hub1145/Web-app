import asyncio
import websockets
import threading
import json

class NewsWSServer:
    """
    A WebSocket server to broadcast news to connected clients.
    """
    def __init__(self, host="localhost", port=8765):
        self.host = host
        self.port = port
        self.clients = set()
        self.server = None
        self.thread = None
        self.loop = None

    async def _register(self, websocket):
        """Adds a client to the set of connected clients."""
        self.clients.add(websocket)
        print(f"[*] New client connected. Total clients: {len(self.clients)}")

    async def _unregister(self, websocket):
        """Removes a client from the set."""
        self.clients.remove(websocket)
        print(f"[*] Client disconnected. Total clients: {len(self.clients)}")

    async def broadcast(self, message: str):
        """Sends a message to all connected clients."""
        if self.clients:
            # websockets.broadcast is a helper that sends a message to an iterable of clients
            await websockets.broadcast(self.clients, message)

    async def _handler(self, websocket, path):
        """
        Handles a new WebSocket connection. Keeps it alive and handles cleanup.
        """
        await self._register(websocket)
        try:
            # Keep the connection open and listen for messages (though we don't expect any from clients)
            async for message in websocket:
                # For now, we just log any message received from a client.
                print(f"[*] Received message from client: {message}")
        finally:
            await self._unregister(websocket)

    def _run_server(self):
        """The target function for the server thread."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        async def main():
            """Starts the server and keeps it running."""
            # websockets.serve is an async context manager
            async with websockets.serve(self._handler, self.host, self.port) as server:
                self.server = server
                print(f"[*] WebSocket News Server started on ws://{self.host}:{self.port}")
                # Keep the server running until stop() is called by cancelling the future
                await asyncio.Future()

        try:
            self.loop.run_until_complete(main())
        except asyncio.CancelledError:
            # This is expected when we stop the loop
            pass
        finally:
            self.loop.close()
            print("[*] WebSocket event loop closed.")

    def start(self):
        """Starts the WebSocket server in a separate daemon thread."""
        if self.thread is None or not self.thread.is_alive():
            self.thread = threading.Thread(target=self._run_server)
            self.thread.daemon = True
            self.thread.start()
            print("[*] WebSocket server thread started.")

    def stop(self):
        """Stops the WebSocket server."""
        if self.loop and self.loop.is_running():
            print("[*] Stopping WebSocket server...")
            # Cancel all running tasks in the loop. This will include the asyncio.Future
            # which will break the `main` function's await.
            tasks = asyncio.all_tasks(loop=self.loop)
            for task in tasks:
                task.cancel()

            # Stop the loop itself
            self.loop.call_soon_threadsafe(self.loop.stop)
            self.thread.join(timeout=2)
            print("[*] WebSocket server stopped.")
        self.thread = None

# Example of how to run the server
if __name__ == '__main__':
    news_server = NewsWSServer()
    news_server.start()
    time.sleep(1) # Give server time to start

    # This is a simple test client to connect and see if messages are received.
    async def test_client():
        uri = f"ws://{news_server.host}:{news_server.port}"
        try:
            async with websockets.connect(uri) as websocket:
                print(f"[*] Test client connected to {uri}")
                # First message is the connection confirmation
                await websocket.recv()
                while True:
                    message = await websocket.recv()
                    print(f"< Received from server: {message}")
        except websockets.ConnectionClosed:
            print("[*] Test client disconnected.")
        except ConnectionRefusedError:
            print("[!] Connection refused. Is the server running?")

    # This function will run in the main thread to send test messages.
    def send_test_messages():
        # Add the test client as a "client" so it receives broadcasts
        client_coro = test_client()
        client_task = asyncio.run_coroutine_threadsafe(client_coro, news_server.loop)

        while news_server.thread and news_server.thread.is_alive():
            time.sleep(5)
            test_message = json.dumps({"headline": "This is a test news flash!", "source": "Test"})
            if news_server.loop and news_server.loop.is_running():
                future = asyncio.run_coroutine_threadsafe(news_server.broadcast(test_message), news_server.loop)
                try:
                    future.result(timeout=2)
                    print(f"> Sent a test message: {test_message}")
                except asyncio.TimeoutError:
                    print("[!] Timeout sending message.")

        client_task.cancel()


    print("Server is running. Test client will connect and listen.")
    print("Press Ctrl+C to stop.")

    try:
        # Keep the main thread alive to see the output
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nProgram terminating.")
    finally:
        news_server.stop()
