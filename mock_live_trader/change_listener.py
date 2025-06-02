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
    old_pairs_path = os.path.join(base_dir, "coin_listings", "current_pairs.json")

    new_pairs = get_path_listing(new_pairs_path)
    old_pairs = get_path_listing(old_pairs_path)

    for pair, new_exchanges in new_pairs.items():
        if pair not in old_pairs:
            print(f"New trading pair detected: {pair}")
            update_old_pairs(old_pairs_path, new_pairs)
            return (pair, new_exchanges)

        old_exchanges = set(old_pairs[pair])
        # Check if there are any new exchanges (not missing ones)
        for exchange in new_exchanges:
            if exchange not in old_exchanges:
                print(f"New exchange detected for pair '{pair}': {exchange}")
                print(f"  Old exchanges: {old_pairs[pair]}")
                print(f"  New exchanges: {new_exchanges}")
                update_old_pairs(old_pairs_path, new_pairs)
                return (pair, new_exchanges)

    print("No new trading pairs or exchanges found.")
    return None

