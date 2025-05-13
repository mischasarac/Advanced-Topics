import requests
import numpy
import os


def get_orderbook(ticker : str):
    url = "https://api.binance.com/api/v3/depth"
    params = {
        "symbol" : ticker,
        "limit" : 2
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        orderbook = response.json()
        print(orderbook)
    except requests.RequestException as e:
        print(f"Error fetching order book: {e}")

get_orderbook("SIGNUSDT")