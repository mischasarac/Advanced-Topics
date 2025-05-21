import requests
import os
import json


class Exchange:
    def __init__(self, ticker):
        self.ticker = self.format_ticker(ticker)
        self.limit = 2

    def get_url(self):
        raise NotImplementedError
    
    def format_ticker(self, ticker):
        return ticker + "USDT"

    def get_params(self):
        return {"symbol": self.ticker, "limit": self.limit}

    def parse_response(self, response_json):
        raise NotImplementedError

    def fetch_orderbook(self):
        try:
            response = requests.get(self.get_url(), params=self.get_params())
            response.raise_for_status()
            data = self.parse_response(response.json())
            return data
        except requests.RequestException as e:
            print(f"Request error for {self.__class__.__name__} - {self.ticker}: {e}")
        except Exception as e:
            print(f"Parsing error for {self.__class__.__name__} - {self.ticker}: {e}")
        return {"bids": [[-1, -1], [-1, -1]], "asks": [[-1, -1], [-1, -1]]}


class Binance(Exchange):
    def get_url(self):
        return "https://api.binance.com/api/v3/depth"

    def parse_response(self, response_json):
        return {
            "asks": response_json['asks'],
            "bids": response_json['bids']
        }


class Bybit(Exchange):
    def get_url(self):
        return "https://api.bybit.com/v5/market/orderbook"

    def get_params(self):
        params = super().get_params()
        params["category"] = "spot"
        return params

    def parse_response(self, response_json):
        result = response_json.get("result")
        if result:
            return {
                "asks": result["a"],
                "bids": result["b"]
            }
        return {"bids": [[-1, -1], [-1, -1]], "asks": [[-1, -1], [-1, -1]]}


class Kucoin(Exchange):
    
    def format_ticker(self, ticker):
        super().format_ticker(ticker)
        return ticker + "-USDT"

    def get_url(self):
        return "https://api.kucoin.com/api/v1/market/orderbook/level2_100"

    def parse_response(self, response_json):
        data = response_json.get("data")
        if data:
            return {
                "asks": data["asks"][0:2],
                "bids": data["bids"][0:2]
            }
        return {"bids": [[-1, -1], [-1, -1]], "asks": [[-1, -1], [-1, -1]]}


EXCHANGE_CLASSES = {
    "binance": Binance,
    "bybit": Bybit,
    "kucoin": Kucoin
}


def get_new_listing_orderbook():
    pairs_path = "/home/mischa/topics/Advanced-Topics/new_listing_detection/pairs.json"
    if not os.path.exists(pairs_path):
        print(f"pairs.json not found at {pairs_path}")
        return

    with open(pairs_path, "r") as f:
        all_pairs = json.load(f)

    for ticker, exchanges in all_pairs.items():
        print(f"{ticker}USDT:")

        for exchange_name in exchanges:
            exchange_class = EXCHANGE_CLASSES.get(exchange_name)
            if not exchange_class:
                print(f" - Unknown exchange: {exchange_name}")
                continue
            exchange_instance = exchange_class(ticker)
            result = exchange_instance.fetch_orderbook()


            print(f" - {exchange_name} - ")
            try:
                print(f"Bids: {result['bids'][0]}, {result['bids'][1]}")
                print(f"Asks: {result['asks'][0]}, {result['asks'][1]}")
            except IndexError:
                print(" - Not enough data to show top 2 bids/asks")


if __name__ == "__main__":
    get_new_listing_orderbook()
