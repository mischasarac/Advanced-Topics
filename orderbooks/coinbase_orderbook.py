import requests

def get_coinbase_orderbook(ticker: str, level: int = 1):
    url = f"https://api.exchange.coinbase.com/products/{ticker}/book"
    params = {
        "level": level
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        orderbook = response.json()
        print(orderbook)
    except requests.RequestException as e:
        print(f"Error fetching Coinbase orderbook: {e}")

# Example usage
get_coinbase_orderbook("SXT-USD", level=1)
