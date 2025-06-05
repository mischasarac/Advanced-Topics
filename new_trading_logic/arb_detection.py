import requests
import os
import json
from get_orderbook import get_orderbook
from new_listing import ListingAggregator
from change_listener import identify_difference
from datetime import datetime, timedelta
import time
import csv


def get_path_listing(filepath: str):
    # Getting file as json
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    else:
        raise FileNotFoundError

EXCHANGES = ["binance", "bybit", "kucoin"]


def detect_arb(new_ticker):
    
    
    # This section is to account for early announcement
    start_time = datetime.now()
    time_wait = timedelta(minutes=2)
    while get_orderbook(new_ticker[1], new_ticker[0]) is None and datetime.now() - start_time < time_wait:
        time.sleep(5)

    # Initiating variables
    best_ask = ("", 100000000)
    best_bid = ("", 0)
    
    # Arbitrarily checking through all exchanges
    for exchange in EXCHANGES:
        orderbook = get_orderbook(new_ticker[1], exchange)
        # If exchange doesn't have such ticker
        if orderbook is None:
            continue
        # print(orderbook)
        if orderbook["bids"][0][0] > best_bid[1]:
            best_bid = (exchange, orderbook["bids"][0][0])
        if orderbook["asks"][0][0] < best_ask[1]:
            best_ask = (exchange, orderbook["asks"][0][0])
    
    print(best_ask)
    print(best_bid)
    print(f"disparity : {best_bid[1] / best_ask[1]}")
    if(best_bid[1] > best_ask[1] * 1.003): 
        return {
            "ticker" : new_ticker[1],
            "long" : best_bid,
            "short" : best_ask
        }
    else:
        print("no arb possible")
        return None

# if __name__ == "__main__":
#     detect_arb()