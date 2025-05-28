import requests
from orderbooks.orderbook import Binance, Bybit, Kucoin
import os
import json
from live_trader.get_orderbook import get_orderbook


def get_path_listing(filepath: str):
    # Getting file as json
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    else:
        raise FileNotFoundError

def identify_difference() -> bool:
    # Detecting a difference between the old listings and the new ones. If new listing detected, resulting orderbooks will be returned

    # Note that only 1 detection will be made. This goes under the assumption (will only profit off) the expectation that only 1 change will 
    # likely have been made in the previous 5 minutes.

    new_pairs_path = "/home/mischa/topics/Advanced-Topics/new_listing_detection/pairs.json"
    old_pairs_path = "/home/mischa/topics/Advanced-Topics/current_pairs.json"
    # For comparison
    new_pairs = get_path_listing(new_pairs_path)
    old_pairs = get_path_listing(old_pairs_path)

    if os.path.exists(old_pairs_path):
        with open(old_pairs_path, "w") as f:
            json.dump(new_pairs, f, indent=2)

    # Track if there are any differences
    found_difference = False

    # Compare new_pairs with old_pairs
    for pair, new_exchanges in new_pairs.items():
        if pair in old_pairs:
            old_exchanges = old_pairs[pair]
            if set(new_exchanges) != set(old_exchanges):
                print(f"Difference found for pair '{pair}':")
                print(f"  Old exchanges: {old_exchanges}")
                print(f"  New exchanges: {new_exchanges}")
                return (pair, new_exchanges)
        else:
            print(f"Pair '{pair}' is new in the new_pairs list.")
            return (pair, new_exchanges)
    
    if not found_difference:
        print("No differences found between new_pairs and old_pairs.")

    return None
    

def detect_arb():
    new_listing = identify_difference()
    if new_listing != None:
        OB = get_orderbook(new_listing[0], new_listing[1])
    else:
        return False
    
    # Detect greater than 0.2% difference
    '''
    *exchange_name* : {
        "bids" : [[a, b], [c, d]],
        "asks" : [[e, f], [g, h]]
    }
    '''

    best_ask = ("", 100000000.0)
    best_bid = ("", 0.0)

    # Seleting best asks and bids in worst-case scenario (low volume in first index)
    if new_listing != None:
        for exchange, orderbook in OB.items():
            # Error handling
            if orderbook['asks'][0][0] == -1: continue
            # Current case
            if float(orderbook['asks'][1][0]) < best_ask[1]:
                best_ask = (exchange, float(orderbook['asks'][1][0]))
            if float(orderbook['bids'][1][0]) > best_bid[1]:
                best_bid = (exchange, float(orderbook['bids'][1][0]))

    # Check for arb opportunity (>0.2% difference)
    print(f"disparity : {best_bid[1] / best_ask[1]}")
    if(best_bid[1] > best_ask[1] * 1.002): 
        return {
            "long" : best_bid,
            "short" : best_ask
        }
    else:
        print("no arb possible")
    return None
    



if __name__ == "__main__":
    detect_arb()