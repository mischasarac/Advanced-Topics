import ccxt
import numpy
import os
import json

exchanges = {
    "binance" : ccxt.binance(),
    "bybit" : ccxt.bybit(),
    "kucoin" : ccxt.kucoin()
}


def get_orderbook(ticker : str, curr_exchanges : list, orderbook_depth=2):
    orderbook = {}
    # print(f"{ticker}:")
    for exchange in curr_exchanges:
        try:
            if(exchange == "kucoin"): curr_ticker = ticker + "/USDT"
            else: curr_ticker = ticker + "USDT"
            request = exchanges[exchange].fetch_order_book(curr_ticker)
            orderbook[exchange] = {
                                    "bids": request["bids"][0:orderbook_depth],
                                    "asks": request["asks"][0:orderbook_depth]
                                  }
            # print(orderbook[exchange])
        except Exception as e:
            print(f"an error occurred: {e}")
    return orderbook
    

# get_orderbook("SOON", ['kucoin', 'bybit', "binance"])