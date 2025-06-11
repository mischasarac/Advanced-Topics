import ccxt
import os
import json


def get_balances(long_exchange: str, short_exchange: str):
    """
    Retrieves the balances for the specified exchanges.
    
    :param long_exchange: Name of the long exchange (e.g., 'binance').
    :param short_exchange: Name of the short exchange (e.g., 'bybit').
    :return: Dictionary containing balances for both exchanges.
    """
    
    cwd = os.getcwd()
    client_info_path = f"{cwd}/client_info.json"
    
    if not os.path.exists(client_info_path):
        raise FileNotFoundError(f"Client info file not found at {client_info_path}")
    
    with open(client_info_path, "r") as f:
        client_info = json.load(f)
    
    if long_exchange not in client_info or short_exchange not in client_info:
        raise ValueError("One or both exchanges not found in client info.")
    
    long_client = ccxt.__dict__[long_exchange](client_info[long_exchange])
    short_client = ccxt.__dict__[short_exchange](client_info[short_exchange])
    
    long_balance = long_client.fetch_balance()
    short_balance = short_client.fetch_balance()
    
    return {
        long_exchange: long_balance['total'],
        short_exchange: short_balance['total']
    }