import requests

def print_all_binance_tickers():
    url = "https://api.binance.com/api/v3/exchangeInfo"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        symbols = [s['symbol'] for s in data['symbols']]
        for symbol in symbols:
            print(symbol)

    except requests.RequestException as e:
        print(f"Error fetching tickers: {e}")

if __name__ == "__main__":
    print_all_binance_tickers()
