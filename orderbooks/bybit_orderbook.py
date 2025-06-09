import requests
import numpy
import os
import ccxt

# def get_all_symbols():
#     url = "https://api.bybit.com/v5/market/instruments-info"
#     params = {
#         "category": "linear"
#     }

#     try:
#         response = requests.get(url, params=params)
#         response.raise_for_status()
#         data = response.json()
#         for entry in data["result"]["list"]:
#             print(entry["symbol"])
#             if "LAUNCHCOIN" in entry["symbol"]:
#                 print("Found:", entry["symbol"])
#     except requests.RequestException as e:
#         print(f"Error: {e}")

# get_all_symbols()


def get_orderbook(ticker: str):
    curr = ccxt.bybit()
    curr_ticker = f"{ticker}USDT"
    ob = curr.fetch_order_book(curr_ticker)

    print(ob)

get_orderbook("SKATE")
