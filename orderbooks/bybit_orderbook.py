import requests
import numpy
import os
import ccxt


def get_orderbook(ticker: str):
    curr = ccxt.bybit()
    curr_ticker = f"{ticker}USDT"
    ob = curr.fetch_order_book(curr_ticker)

    print(ob)

get_orderbook("SKATE")
