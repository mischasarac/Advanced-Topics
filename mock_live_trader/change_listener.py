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
    cwd = os.getcwd()
    new_pairs_path = f"{cwd}/coin_listings/new_pairs.json"
    old_pairs_path = f"{cwd}/coin_listings/current_pairs.json"

    # Load new and old listings
    new_pairs = get_path_listing(new_pairs_path)
    old_pairs = get_path_listing(old_pairs_path)

    # Track changes
    changes = []

    # Check for new pairs or changed exchanges
    for pair, new_exchanges in new_pairs.items():
        if pair in old_pairs:
            old_exchanges = old_pairs[pair]
            if set(new_exchanges) != set(old_exchanges):
                print(f"Difference found for pair '{pair}':")
                print(f"  Old exchanges: {old_exchanges}")
                print(f"  New exchanges: {new_exchanges}")
                changes.append((pair, new_exchanges))
        else:
            print(f"Pair '{pair}' is new in the new_pairs list.")
            changes.append((pair, new_exchanges))

    # Update old_pairs file with new_pairs
    if changes:
        with open(old_pairs_path, "w") as f:
            json.dump(new_pairs, f, indent=2)
    else:
        print("No differences found between new_pairs and old_pairs.")

    return changes

# Example usage
identify_difference()
