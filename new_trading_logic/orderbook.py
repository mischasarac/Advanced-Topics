import requests
import os
import json


class Exchange:
    def __init__(self):
        self.limit = 3

    def get_url(self):
        raise NotImplementedError
    
    def format_ticker(self, ticker):
        return ticker + "USDT"

    def get_params(self):
        return {"symbol": self.ticker, "limit": self.limit}

    def parse_response(self, response_json):
        raise NotImplementedError
    
    def _convert_orderbook(self, raw_orderbook):
        return {
            "asks": [[float(p), float(v)] for p, v in raw_orderbook.get("asks", [])[:self.limit]],
            "bids": [[float(p), float(v)] for p, v in raw_orderbook.get("bids", [])[:self.limit]]
        }


    def fetch_orderbook(self, ticker):
        try:
            self.ticker = self.format_ticker(ticker)
            response = requests.get(self.get_url(), params=self.get_params())
            response.raise_for_status()
            data = self.parse_response(response.json())
            return self._convert_orderbook(data)
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


class Bybit(Exchange):
    def get_url(self):
        return "https://api.bybit.com/v5/market/orderbook"

    def get_params(self):
        params = super().get_params()
        params["category"] = "linear"
        return params

    def parse_response(self, response_json):
        result = response_json.get("result")
        if result:
            return {
                "asks": result["a"],
                "bids": result["b"]
            }
        return None


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
                "asks": data["asks"][:self.limit],
                "bids":  data["bids"][:self.limit]
            }
        return None




if __name__ == "__main__":
    bybit = Bybit()
    ob = bybit.fetch_orderbook("RESOLV")
    print(ob)
