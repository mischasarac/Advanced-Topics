import time
from scan_listings import ListingAggregator
from change_listener import identify_difference
from get_orderbook import get_orderbook
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
        print(f"New listing detected: {change[0]} on exchanges {change[1]}")
        print(f"Orderbook for {change[0]}: {json.dumps(orderbook, indent=2)}")
    else:
        print("No new listings detected.")
    # Wait for 5 minutes before the next run
    time.sleep(300)  # 5 minutes in seconds