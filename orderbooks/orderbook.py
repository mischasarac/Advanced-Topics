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



# if __name__ == "__main__":
#     get_new_listing_orderbook()
