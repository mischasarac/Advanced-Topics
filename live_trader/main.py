import time
from scan_listings import ListingAggregator



def run():
    # Save newest listings to new_pairs.json
    aggregator = ListingAggregator()
    aggregator.gather_listings()