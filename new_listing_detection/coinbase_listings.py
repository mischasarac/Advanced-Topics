import requests
import json
import os

# Endpoint to get all trading pairs (products)
COINBASE_PRODUCTS_URL = "https://api.exchange.coinbase.com/products"
LOCAL_FILE = "coinbase_products.json"

def fetch_current_products():
    response = requests.get(COINBASE_PRODUCTS_URL)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch products: {response.status_code} - {response.text}")

def load_previous_products():
    if os.path.exists(LOCAL_FILE):
        with open(LOCAL_FILE, "r") as f:
            return json.load(f)
    return []

def save_current_products(products):
    with open(LOCAL_FILE, "w") as f:
        json.dump(products, f, indent=2)

def find_new_listings(old_products, new_products):
    old_ids = {p["id"] for p in old_products}
    return [p for p in new_products if p["id"] not in old_ids]

def main():
    print("Checking for new Coinbase listings...")
    old_products = load_previous_products()
    new_products = fetch_current_products()
    
    new_listings = find_new_listings(old_products, new_products)

    if new_listings:
        print("🔔 New listings found:")
        for p in new_listings:
            print(f"- {p['id']} (Base: {p['base_currency']}, Quote: {p['quote_currency']})")
    else:
        print("No new listings.")

    # save_current_products(new_products) DON'T DO THIS UNLESS TIMEFRAME HAS PASSED. CURRENT DATE 8/5/25 (D/M/Y)

if __name__ == "__main__":
    main()
