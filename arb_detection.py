import requests
import numpy
import os



def get_order_book(ticker : str):
    url = "https://api.bybit.com/v5/market/orderbook"
    params = {
        "category" : "spot",
        "symbol" : ticker,
        "limit" : 2
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        print(response.json())
    except requests.RequestException as e:
        print(f"Error: {e}")

get_order_book("HAEDALUSDT")