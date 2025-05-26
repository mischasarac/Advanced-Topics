import requests
import numpy
import os

def get_all_symbols():
    url = "https://api.bybit.com/v5/market/instruments-info"
    params = {
        "category": "linear"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        for entry in data["result"]["list"]:
            print(entry["symbol"])
            if "LAUNCHCOIN" in entry["symbol"]:
                print("Found:", entry["symbol"])
    except requests.RequestException as e:
        print(f"Error: {e}")

get_all_symbols()


def get_orderbook(ticker: str):
    url = "https://api.bybit.com/v5/market/orderbook"
    params = {
        "category": "linear",
        "symbol": ticker,
        "limit": 2
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        print(response.json())
    except requests.RequestException as e:
        print(f"Error: {e}")

get_orderbook("LAUNCHCOINUSDT")
