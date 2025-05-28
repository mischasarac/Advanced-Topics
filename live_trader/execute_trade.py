import ccxt
import os
import json



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

# Execute long or short based on input parameters
def execute_arb(ticker: str, long_exchange: str, short_exchange: str, amount: dict):

    client_info = get_client_info()

    long_class = get_exchange_client(long_exchange, client_info)
    short_class = get_exchange_client(short_exchange, client_info)

    long_exchange_liquid = amount[long_exchange]
    short_exchange_liquid = amount[short_exchange]

    max_tradable = min(long_exchange_liquid, short_exchange_liquid)

    # Perform long after short as a safety measure. More likely that the long will be executed first.
    if max_tradable <= 0:
        print(f"Insufficient liquidity to execute trade for {ticker} on {long_exchange} or {short_exchange}.")
        return
    print(f"Executing arbitrage for {ticker} with max tradable amount: {max_tradable} USDT")
    # Check if the ticker is valid
    if not ticker:
        print(f"Invalid ticker: {ticker}")
        return

    # Executing short with ccxt
    try:
        short_order = short_class.create_market_sell_order(ticker + '/USDT', max_tradable)
        print(f"Short order executed on {short_exchange}: {short_order}")
    except Exception as e:
        print(f"Error executing short order on {short_exchange}: {e}")
        return
    # Executing long with ccxt
    try:
        long_order = long_class.create_market_buy_order(ticker + '/USDT', max_tradable)
        print(f"Long order executed on {long_exchange}: {long_order}")
    except Exception as e:
        print(f"Error executing long order on {long_exchange}: {e}")
        return
    

