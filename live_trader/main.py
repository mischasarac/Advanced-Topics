import time
from scan_listings import ListingAggregator
from change_listener import identify_difference
from get_orderbook import get_orderbook
from execute_trade import execute_arb
from get_balances import get_balances
import json
import os
from datetime import timedelta



def run():
    # Save newest listings to new_pairs.json
    aggregator = ListingAggregator()
    aggregator.gather_listings()

    # Identify changes in listings
    change = identify_difference()

    if change:
        orderbook = get_orderbook(change[0], change[1])

        if orderbook is not None:

            # Get amount (USDT) within each exchange
            long_exchange = orderbook["long"][0]
            short_exchange = orderbook["short"][0]

            balances = get_balances(long_exchange, short_exchange)

            execute_arb(ticker=change, long_exchange=orderbook["long"][0], 
                        short_exchange=orderbook["short"][0], balances=balances)
            
    # Wait for 5 minutes before the next run
    time.sleep(300)  # 5 minutes in seconds