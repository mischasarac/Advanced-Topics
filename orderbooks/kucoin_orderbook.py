import requests

def get_orderbook(ticker: str):
    url = "https://api.kucoin.com/api/v1/market/orderbook/level2_100"
    params = {
        "symbol": ticker,
        "limit" : 2
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        orderbook = response.json()
        asks = orderbook.get('data', {})['asks']
        bids = orderbook.get('data', {})['bids']
        print(f"asks : {asks[0]}, {asks[1]}")
        print(f"bids : {bids[0]}, {bids[1]}")
    except requests.RequestException as e:
        print(f"Error with orderbook: {e}")

get_orderbook("SXT-USDT")
