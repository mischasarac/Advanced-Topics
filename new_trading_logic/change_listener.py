import json
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

def identify_difference():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    new_pairs_path = os.path.join(base_dir, "coin_listings", "new_pairs.json")
    old_pairs_path = os.path.join(base_dir, "coin_listings", "old_pairs.json")

    new_pairs = get_path_listing(new_pairs_path)
    old_pairs = get_path_listing(old_pairs_path)

    for exchange, listings in new_pairs.items():
        for listing in listings:
            if listing not in set(old_pairs[exchange]):
                print(f"New ticker detected for pair '{exchange}': {listing}")
                update_old_pairs(old_pairs_path, new_pairs)
                return (exchange, listing)

    print("No new trading pairs or exchanges found.")
    return None


