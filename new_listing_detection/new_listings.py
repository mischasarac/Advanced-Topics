import requests
from datetime import datetime
import json
import os
import re
import selenium

class ExchangeBase:
    def __init__(self, name, url, params, headers):
        self.name = name
        self.url = url
        self.params = params
        self.headers = headers
        # Listings should be stored as a set in the case of multiples
        self.tickers = set()
    
    def get_titles(self):
        raise NotImplementedError("Subclasses must implement get_titles")

    def fetch_data(self):
        titles = self.get_titles()

        for title in titles:
            current_ticker = self.extract_ticker(title)
            if current_ticker:
                self.tickers.add(current_ticker[0])
        return self.tickers

    def extract_ticker(self, title):
        if not title.strip():
            return []

        title_parts = title.split()

        # Case: "New Listing: XYZ/USDT will be listed on Bybit"
        if title_parts[0] == "New" and (title_parts[1].lower() == "listing" or title_parts[1].lower() == "listings"):
            # Handles both "New Listing: XYZ/USDT" and "New Listing XYZ/USDT"
            raw_ticker = title_parts[3] if title_parts[2] == ":" else title_parts[2]
            # Remove USDT or /USDT suffix
            cleaned_ticker = re.sub(r'(/?USDT)$', '', raw_ticker, flags=re.IGNORECASE)
            return [cleaned_ticker]

        # Fallback case: match tickers in parentheses like "Coin XYZ (ABC)"
        tickers = re.findall(r'\(([^)]+)\)', title)
        cleaned = [re.sub(r'(/?USDT)$', '', t, flags=re.IGNORECASE) for t in tickers]
        return cleaned




class BinanceExchange(ExchangeBase):
    # Implement last
    def get_titles(self):
        try:
            response = requests.get(self.url, params=self.params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            articles = data.get('data', {}).get('catalogs', [])[0].get('articles', [])
            result = []
            for article in articles:
                result.append(article.get("title"))
            return result
        except requests.RequestException as e:
            print(f"Error with fetching data : {e}")
    

class BybitExchange(ExchangeBase):
    def get_titles(self):
        try:
            response = requests.get(self.url, params=self.params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            articles = data.get("result", {}).get("list")
            result = []
            for article in articles:
                if article.get("type", {}).get("key") == "new_crypto":
                    result.append(article.get("title", ""))
                
            return result
        except requests.RequestException as e:
            print(f"Error fetching data from {self.name}: {e}")
            return []



class KucoinExchange(ExchangeBase):
    def get_titles(self):
        try:
            response = requests.get(self.url, params=self.params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            articles = data["data"]["items"]
            result = []
            for article in articles:
                result.append(article.get("annTitle", ""))
            return result
        except requests.RequestException as e:
            print(f"Error with fetching data : {e}")
            return []


class ListingAggregator:
    def __init__(self):
        self.exchanges = [
            BinanceExchange(
                "binance",
                "https://www.binance.com/bapi/composite/v1/public/cms/article/list/query",
                {
                    "type": 1, "catalogId": 48, "pageNo": 1, "pageSize": 20
                },
                {
                    "User-Agent": "Mozilla/5.0",
                    "Referer": "https://www.binance.com/en/support/announcement/c-48",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept": "application/json, text/plain, */*"
                }
            ),
            BybitExchange(
                "bybit",
                "https://api.bybit.com/v5/announcements/index",
                {"locale": "en-US", "page": 1, "limit": 100},
                {}
            ),
            KucoinExchange(
                "kucoin",
                "https://api.kucoin.com/api/v3/announcements",
                {"annType": "new-listings", "lang": "en_US", "pageSize": 10},
                {}
            )
        ]
        self.listings = {}

    def gather_listings(self):
        seen = {}
        for exchange in self.exchanges:
            data = exchange.fetch_data()
            print(data)
            if not data:
                continue
            listings = exchange.tickers
            self.listings[exchange.name] = listings
            for ticker in listings:
                seen.setdefault(ticker, []).append(exchange.name)

        self._save_cross_listings(seen)

    def _save_cross_listings(self, seen):
        cross_listed = {t: exs for t, exs in seen.items() if len(exs) > 1}
        for token, exchanges in cross_listed.items():
            print(f"{token} : {exchanges}")

        path = "/home/mischa/topics/Advanced-Topics/new_listing_detection/pairs.json"
        with open(path, "w") as f:
            json.dump(cross_listed, f, indent=2)


if __name__ == "__main__":
    aggregator = ListingAggregator()
    aggregator.gather_listings()
