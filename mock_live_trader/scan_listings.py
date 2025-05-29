import json
import os
import re
from datetime import datetime

import requests


class ExchangeBase:
    """
    Base class for cryptocurrency exchange data fetching.
    """

    def __init__(self, name, url, params, headers):
        """
        Initialize an exchange with its name, API URL, parameters, and headers.
        """
        self.name = name
        self.url = url
        self.params = params
        self.headers = headers
        self.tickers = set()

    def get_titles(self):
        """
        Abstract method to be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement get_titles")

    def fetch_data(self):
        """
        Fetches data from the exchange API and extracts tickers from titles.
        """
        titles = self.get_titles()
        for title in titles:
            current_ticker = self.extract_ticker(title)
            if current_ticker:
                self.tickers.add(current_ticker[0])
        return self.tickers

    def extract_ticker(self, title):
        """
        Extracts ticker symbols from titles.
        """
        if not title.strip():
            return []

        title_parts = title.split()

        if title_parts[0] == "New" and (title_parts[1].lower() == "listing" or title_parts[1].lower() == "listings"):
            raw_ticker = title_parts[3] if title_parts[2] == ":" else title_parts[2]
            cleaned_ticker = re.sub(r'(/?USDT)$', '', raw_ticker, flags=re.IGNORECASE)
            return [cleaned_ticker]

        tickers = re.findall(r'\(([^)]+)\)', title)
        cleaned = [re.sub(r'(/?USDT)$', '', t, flags=re.IGNORECASE) for t in tickers]
        return cleaned


class BinanceExchange(ExchangeBase):
    """
    Exchange class for Binance exchange.
    """

    def get_titles(self):
        """
        Fetches titles from Binance API.
        """
        try:
            response = requests.get(self.url, params=self.params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            articles = data.get('data', {}).get('catalogs', [])[0].get('articles', [])
            result = [article.get("title") for article in articles]
            return result
        except requests.RequestException as e:
            print(f"Error with fetching data from {self.name}: {e}")
            return []


class BybitExchange(ExchangeBase):
    """
    Exchange class for Bybit exchange.
    """

    def get_titles(self):
        """
        Fetches titles from Bybit API.
        """
        try:
            response = requests.get(self.url, params=self.params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            articles = data.get("result", {}).get("list", [])
            result = [article.get("title", "") for article in articles if article.get("type", {}).get("key") == "new_crypto"]
            return result
        except requests.RequestException as e:
            print(f"Error fetching data from {self.name}: {e}")
            return []


class KucoinExchange(ExchangeBase):
    """
    Exchange class for Kucoin exchange.
    """

    def get_titles(self):
        """
        Fetches titles from Kucoin API.
        """
        try:
            response = requests.get(self.url, params=self.params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            articles = data["data"]["items"]
            result = [article.get("annTitle", "") for article in articles]
            return result
        except requests.RequestException as e:
            print(f"Error with fetching data from {self.name}: {e}")
            return []


class ListingAggregator:
    """
    Aggregates listings from multiple exchanges.
    """

    def __init__(self):
        """
        Initializes the listing aggregator with exchange instances.
        """
        self.exchanges = [
            BinanceExchange(
                "binance",
                "https://www.binance.com/bapi/composite/v1/public/cms/article/list/query",
                {"type": 1, "catalogId": 48, "pageNo": 1, "pageSize": 20},
                {"User-Agent": "Mozilla/5.0", "Referer": "https://www.binance.com/en/support/announcement/c-48",
                 "Accept-Language": "en-US,en;q=0.9", "Accept": "application/json, text/plain, */*"}
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
        """
        Gathers listings from all exchanges and saves cross-listings.
        """
        seen = {}
        for exchange in self.exchanges:
            data = exchange.fetch_data()
            if not data:
                continue
            listings = exchange.tickers
            self.listings[exchange.name] = listings
            for ticker in listings:
                seen.setdefault(ticker, []).append(exchange.name)

        self._save_cross_listings(seen)

    def _save_cross_listings(self, seen):
        """
        Saves cross-listed tokens to a JSON file.
        """
        cross_listed = {t: exs for t, exs in seen.items() if len(exs) > 1}

        path = f"{os.getcwd()}/coin_listings/new_pairs.json"
        with open(path, "w") as f:
            json.dump(cross_listed, f, indent=2)

