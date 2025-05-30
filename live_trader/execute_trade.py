import ccxt
import os
import json
import time


# client info
def get_client_info():
    """
    Retrieves client information from a JSON file.
    
    :return: Dictionary containing client information.
    """
    cwd = os.getcwd()
    client_info_path = f"{cwd}/client_info.json"
    
    if os.path.exists(client_info_path):
        with open(client_info_path, "r") as f:
            return json.load(f)
    else:
        raise FileNotFoundError(f"Client info file not found at {client_info_path}")
    
def get_exchange_client(exchange_name: str, client_info: dict):
    """
    Retrieves the exchange client based on the exchange name.
    
    :param exchange_name: Name of the exchange (e.g., 'binance', 'bybit', 'kucoin').
    :return: ccxt exchange client instance.
    """
    
    if exchange_name not in client_info:
        raise ValueError(f"Exchange '{exchange_name}' not found in client info.")
    
    api_key = client_info[exchange_name].get("api_key")
    api_secret = client_info[exchange_name].get("api_secret")
    if not api_key or not api_secret:
        raise ValueError(f"API key or secret for '{exchange_name}' is missing.")
    exchange_class = getattr(ccxt, exchange_name)
    return exchange_class({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True
    })

symbol_converstion = {
    "bybit" : "USDT",
    "binance" : "USDT",
    "kucoin" : "/USDT"
}

def execute_arb(ticker: str, long_exchange: str, short_exchange: str, amount: dict):
    client_info = get_client_info()

    long_client = get_exchange_client(long_exchange, client_info)
    short_client = get_exchange_client(short_exchange, client_info)

    # Standardize ticker (symbol)
    ticker = ticker.upper()
    short_symbol = ticker + symbol_converstion[short_exchange]
    long_symbol = ticker + symbol_converstion[long_exchange]
    # symbol = f"{ticker}/USDT"

    long_balance = amount[long_exchange]
    short_balance = amount[short_exchange]

    max_trade_amount = min(long_balance, short_balance)
    if max_trade_amount <= 0:
        print("No valid trade amount to execute.")
        return

    # Fetch order books
    try:
        long_orderbook = long_client.fetch_order_book(long_symbol)
        short_orderbook = short_client.fetch_order_book(short_symbol)
    except Exception as e:
        print(f"Failed to fetch order books: {e}")
        return

    long_price = long_orderbook['asks'][0][0]
    short_price = short_orderbook['bids'][0][0]

    if not long_price or not short_price:
        print("Invalid prices retrieved.")
        return

    # Calculate the trade size in asset (e.g., BTC)
    long_asset_amount = max_trade_amount / long_price
    short_asset_amount = max_trade_amount / short_price

    try:
        print(f"Placing SHORT (sell) {short_asset_amount:.6f} {ticker} at ~{short_price:.2f} on {short_exchange}")
        short_order = short_client.create_market_sell_order(short_symbol, short_asset_amount)

        print(f"Placing LONG (buy) {long_asset_amount:.6f} {ticker} at ~{long_price:.2f} on {long_exchange}")
        long_order = long_client.create_market_buy_order(long_symbol, long_asset_amount)
        time.sleep(1)  # small delay to reduce risk of rate limits
    except Exception as e:
        print(f"Trade execution failed: {e}")
        return

    print("Trade executed successfully.")
    return {
        "long": {
            "exchange": long_exchange,
            "symbol": long_symbol,
            "amount": long_asset_amount,
            "price": long_price,
            "order_id": long_order.get('id')
        },
        "short": {
            "exchange": short_exchange,
            "symbol": short_symbol,
            "amount": short_asset_amount,
            "price": short_price,
            "order_id": short_order.get('id')
        }
    }


def close_position(position: dict):
    """
    Closes the arbitrage position by reversing the trades.
    
    :param position: Dictionary containing 'long' and 'short' positions with exchange, symbol, amount.
    """
    if not position or 'long' not in position or 'short' not in position:
        print("Invalid position format.")
        return

    client_info = get_client_info()

    long_data = position['long']
    short_data = position['short']

    try:
        # Get clients
        long_client = get_exchange_client(long_data['exchange'], client_info)
        short_client = get_exchange_client(short_data['exchange'], client_info)

        # Close LONG (i.e., SELL)
        print(f"Closing LONG: Selling {long_data['amount']:.6f} {long_data['symbol']} on {long_data['exchange']}")
        long_close = long_client.create_market_sell_order(
            symbol=long_data['symbol'],
            amount=long_data['amount']
        )

        time.sleep(1)

        # Close SHORT (i.e., BUY)
        print(f"Closing SHORT: Buying {short_data['amount']:.6f} {short_data['symbol']} on {short_data['exchange']}")
        short_close = short_client.create_market_buy_order(
            symbol=short_data['symbol'],
            amount=short_data['amount']
        )

    except Exception as e:
        print(f"Failed to close position: {e}")
        return

    print("Position closed successfully.")
    return {
        "long_close": {
            "exchange": long_data['exchange'],
            "symbol": long_data['symbol'],
            "amount": long_data['amount'],
            "order_id": long_close.get('id')
        },
        "short_close": {
            "exchange": short_data['exchange'],
            "symbol": short_data['symbol'],
            "amount": short_data['amount'],
            "order_id": short_close.get('id')
        }
    }
