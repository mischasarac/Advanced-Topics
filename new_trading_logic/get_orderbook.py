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

    except Exception as e:
        print(f"An error occurred while fetching from {exchange}: {e}")
        return None