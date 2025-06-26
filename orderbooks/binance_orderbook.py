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
        return None


class Binance(Exchange):
    def get_url(self):
        return "https://api.binance.com/api/v3/depth"

    def parse_response(self, response_json):
        if response_json:
            return {
                "asks": response_json['asks'],
                "bids": response_json['bids']
            }
        return None


if __name__ == "__main__":
    binance = Binance()
    