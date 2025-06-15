import ccxt
import json
from orderbook import Binance, Bybit, Kucoin

exchanges = {
    "binance": Binance(),
    "bybit": Bybit(),
    "kucoin": Kucoin()
}

def get_orderbook(ticker: str, exchange: str, orderbook_depth=3):
    orderbook = {}
    try:        
        request = exchanges[exchange].fetch_orderbook(ticker)
        
        orderbook = {
            "bids": request["bids"][:orderbook_depth],
            "asks": request["asks"][:orderbook_depth]
        }

        return orderbook

    except ccxt.NetworkError as e:
        print(f"Network error occurred while fetching from {exchange}: {e}")
        # Handle network errors, maybe retry or log appropriately
    except ccxt.ExchangeError as e:
        print(f"Exchange error occurred while fetching from {exchange}: {e}")
        # Handle specific exchange errors, such as symbol not found
    except Exception as e:
        print(f"An unexpected error occurred while fetching from {exchange}: {e}")
        # Handle any other unexpected errors
    return None