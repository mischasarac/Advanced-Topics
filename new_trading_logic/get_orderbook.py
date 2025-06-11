import ccxt
import json

exchanges = {
    "binance": ccxt.binance(),
    "bybit": ccxt.bybit(),
    "kucoin": ccxt.kucoin()
}

def get_orderbook(ticker: str, exchange: str, orderbook_depth=3):
    orderbook = {}
    try:
        # Format the symbol correctly for each exchange
        if exchange == "kucoin":
            curr_ticker = f"{ticker}/USDT"
        else:
            curr_ticker = f"{ticker}USDT"
        
        # print(f"Querying: {curr_ticker} on {exchange}")
        request = exchanges[exchange].fetch_order_book(curr_ticker)
        
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