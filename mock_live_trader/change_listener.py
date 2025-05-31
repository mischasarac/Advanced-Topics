import json
import os



def get_path_listing(filepath: str):
    # Getting file as json
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    else:
        raise FileNotFoundError


def identify_difference():
    # Detecting a difference between the old listings and the new ones. If new listing detected, resulting orderbooks will be returned

    # Note that only 1 detection will be made. This goes under the assumption (will only profit off) the expectation that only 1 change will 
    # likely have been made in the previous 5 minutes.

    cwd = os.getcwd()

    new_pairs_path = f"{cwd}/coin_listings/new_pairs.json"
    old_pairs_path = f"{cwd}/coin_listings/current_pairs.json"
    # For comparison
    new_pairs = get_path_listing(new_pairs_path)
    old_pairs = get_path_listing(old_pairs_path)

    # Track if there are any differences
    found_difference = False

    # Compare new_pairs with old_pairs
    for pair, new_exchanges in new_pairs.items():
        if pair in old_pairs:
            old_exchanges = old_pairs[pair]
            for exchange in new_exchanges:
                if exchange not in set(old_exchanges):
                    print(f"Difference found for pair '{pair}':")
                    print(f"  Old exchanges: {old_exchanges}")
                    print(f"  New exchanges: {new_exchanges}")
                    if os.path.exists(old_pairs_path):
                        with open(old_pairs_path, "w") as f:
                            json.dump(new_pairs, f, indent=2)
                    return (pair, new_exchanges)
        else:
            if os.path.exists(old_pairs_path):
                with open(old_pairs_path, "w") as f:
                    json.dump(new_pairs, f, indent=2)
            print(f"Pair '{pair}' is new in the new_pairs list.")
            return (pair, new_exchanges)
    
    if not found_difference:
        print("No differences found between new_pairs and old_pairs.")

    return None