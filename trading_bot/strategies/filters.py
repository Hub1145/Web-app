from typing import List, Dict
from trading_bot.brokers.tradestation_api import TradeStationAPI

def apply_filters(symbols: List[str], api_client: TradeStationAPI) -> List[str]:
    """
    Applies pre-trading filters to a list of stock symbols.

    Filters include:
    - Market Cap > $2 Billion
    - Price > $1.00
    - Average Volume > 750,000
    - Current Volume > 1,000,000

    Note: Market Cap and Average Volume might not be available in all
    quote endpoints. This function assumes they are, or that they can be
    derived. The implementation here is based on a typical quote structure.

    :param symbols: A list of stock symbols to screen.
    :param api_client: An instance of the broker API client.
    :return: A list of symbols that pass all filter criteria.
    """
    if not symbols:
        return []

    print(f"Applying filters to {len(symbols)} symbols...")

    try:
        # The get_quote method in the TradeStationAPI can handle a list of symbols
        quotes_data = api_client.get_quote(symbols)
        if not quotes_data or "Quotes" not in quotes_data:
            print("[!] Could not retrieve quotes for filtering.")
            return []

        quotes = quotes_data["Quotes"]
    except Exception as e:
        print(f"[!] Error fetching quotes for filtering: {e}")
        return []

    filtered_symbols = []
    for quote in quotes:
        symbol = quote.get("Symbol")
        try:
            # --- Filter Criteria ---
            # Most APIs provide MarketCap in dollars, Volume as an integer.

            # 1. Price > $1
            last_price = float(quote.get("Last", 0))
            if last_price <= 1.0:
                continue

            # 2. Market Cap > $2B
            # Assuming MarketCap is provided in the quote. If not, this check will fail.
            market_cap = float(quote.get("MarketCap", 0))
            if market_cap <= 2_000_000_000:
                continue

            # 3. Average Volume > 750,000
            # 'AverageVolume' is a common field in quote data.
            avg_volume = int(quote.get("AverageVolume", 0))
            if avg_volume <= 750_000:
                continue

            # 4. Current Volume > 1,000,000
            current_volume = int(quote.get("Volume", 0))
            if current_volume <= 1_000_000:
                continue

            # If all checks pass, add the symbol to the list
            filtered_symbols.append(symbol)

        except (ValueError, TypeError) as e:
            # This can happen if a field is missing or not in the expected format.
            print(f"[!] Warning: Could not process quote for {symbol}. Data: {quote}. Error: {e}")
            continue

    print(f"Filtering complete. {len(filtered_symbols)} symbols passed.")
    return filtered_symbols
