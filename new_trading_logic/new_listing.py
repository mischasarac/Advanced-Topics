import json
import os
import re
from datetime import datetime
import pytz  # Import pytz for timezone handling
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
        self.tickers = dict()

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
            current_ticker = self.extract_ticker(title[0])
            if current_ticker:
                # Release - 30000 for 30 second early trigger
                self.tickers[current_ticker[0]] = {
                                                    "release" : (title[1].timestamp() * 1000) - 30000, 
                                                    "scan_time" : title[2],
                                                    "exchange" : self.name
                                                  }
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
            # print(data)
            articles = data.get('data', {}).get('catalogs', [])[0].get('articles', [])
            result = [(article.get("title"), datetime.now(), 300) for article in articles]
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
            result = [(article.get("title", ""), datetime.now(), 60) for article in articles if article.get("type", {}).get("key") == "new_crypto"]
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
        Fetches titles from Kucoin API and parses announcement time into local datetime.
        """
        try:
            response = requests.get(self.url, params=self.params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            articles = data["data"]["items"]
            result = []

            for article in articles:
                ann_title = article.get("annTitle", "")
                ann_desc = article.get("annDesc", "")  # e.g., "Trading: 13:00 on June 10, 2025 (UTC)"

                try:
                    # Match pattern in annDesc
                    match = re.search(r'Trading:\s*(\d{2}:\d{2}) on ([A-Za-z]+ \d{1,2}, \d{4}) \(UTC\)', ann_desc)
                    if not match:
                        result.append((ann_title, datetime.now(), 60))
                        continue
                    
                    time_str = match.group(1)           # '13:00'
                    date_str = match.group(2)           # 'June 10, 2025'
                    full_str = f"{time_str} {date_str}" # '13:00 June 10, 2025'

                    # Parse UTC datetime
                    utc_dt = datetime.strptime(full_str, "%H:%M %B %d, %Y")
                    utc_dt = utc_dt.replace(tzinfo=pytz.utc)

                    # Convert to local timezone
                    local_tz = pytz.timezone('Australia/Adelaide')
                    local_dt = utc_dt.astimezone(local_tz)

                    # Strip tzinfo to make it consistent with datetime.now()
                    naive_local_dt = local_dt.replace(tzinfo=None)

                    result.append((ann_title, naive_local_dt, 60))
                except Exception as e:
                    print(f"Error parsing announcement time: {e}")

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
            # BinanceExchange(
            #     "binance",
            #     "https://www.binance.com/bapi/composite/v1/public/cms/article/list/query",
            #     {"type": 1, "catalogId": 48, "pageNo": 1, "pageSize": 20},
            #     {"User-Agent": "Mozilla/5.0", "Referer": "https://www.binance.com/en/support/announcement/c-48",
            #      "Accept-Language": "en-US,en;q=0.9", "Accept": "application/json, text/plain, */*"}
            # ),
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
        # For each exchange, combining listing, listing time, and hours spent requesting.
        for exchange in self.exchanges:
            seen[exchange.name] = []
            data = exchange.fetch_data()
            if not data:
                continue
            seen[exchange.name] = exchange.tickers
            # print(seen)

        self._save_cross_listings(seen)

    def _save_cross_listings(self, seen):
        """
        Saves cross-listed tokens to a JSON file.
        """
        # print(seen)

        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, "coin_listings", "new_pairs.json")
        with open(path, "w") as f:
            json.dump(seen, f, indent=2)

if __name__ == "__main__":
    la = ListingAggregator()
    la.gather_listings()