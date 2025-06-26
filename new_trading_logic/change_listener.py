import json
from datetime import datetime
import os

def get_path_listing(filepath: str):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    else:
        raise FileNotFoundError(f"File not found: {filepath}")

def update_old_pairs(old_pairs_path, new_pairs):
    with open(old_pairs_path, "w") as f:
        json.dump(new_pairs, f, indent=2)

def detect_upcoming(upcoming, upcoming_path):
    if upcoming.items():
        for ticker, details in upcoming.items():
            if details["release"] < datetime.now().timestamp() * 1000:
                # Remove from dict
                upcoming.pop(ticker)
                update_old_pairs(upcoming_path, upcoming)
                return (details["exchange"], ticker, details["scan_time"])
    update_old_pairs(upcoming_path, upcoming)
    return None

def identify_difference():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    new_pairs_path = os.path.join(base_dir, "coin_listings", "new_pairs.json")
    old_pairs_path = os.path.join(base_dir, "coin_listings", "old_pairs.json")
    upcoming_path = os.path.join(base_dir, "coin_listings", "upcoming.json")

    new_pairs = get_path_listing(new_pairs_path)
    old_pairs = get_path_listing(old_pairs_path)
    upcoming = get_path_listing(upcoming_path)

    for exchange, listings in new_pairs.items():
        for listing, listing_info in listings.items():
            if listing not in old_pairs[exchange]:
                print(f"New ticker detected for pair '{exchange}': {listing}")
                update_old_pairs(old_pairs_path, new_pairs)
                upcoming[listing] = listing_info
    
    return detect_upcoming(upcoming=upcoming, upcoming_path=upcoming_path)                


if __name__ == "__main__":
    identify_difference()