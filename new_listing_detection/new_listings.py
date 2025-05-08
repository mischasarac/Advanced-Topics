import requests
from datetime import datetime
import re
import numpy
import json


EXCHANGE_INFO = {
    "binance" : {
        "url" : "https://www.binance.com/bapi/composite/v1/public/cms/article/list/query",
        "params" : {
            "type": 1,
            "catalogId": 48,  # Catalog ID for new listings
            "pageNo": 1,
            "pageSize": 50
        },
        "function" : binance_extraction()
    },
    "bybit" : {
        "url" : "https://api.bybit.com/v5/announcements/index",
        "params" : {
            "locale": "en-US",
            "page": 1,
            "limit": 100
        },
        "function" : binance_extraction()
    },
    "coinbase" : {
        "url" : "https://api.exchange.coinbase.com/products",
        "params" : {},
        "function" : binance_extraction()
    },
    "kucoin" : {
        "url" : "https://api.kucoin.com/api/v3/announcements",
        "params" : {
            "annType": "new-listings",
            "lang": "en_US",
            "pageSize": 10
        },
        "function" : binance_extraction()
    }
}


def extract_ticker(title : str) -> str:
    title_parts = title.split()
    # for bybit
    if title_parts[0] == "New" and (title_parts[1] == "listing" or title_parts[1] == "Listing"):
        raw_ticker = title_parts[3] if title_parts[2] == ":" else title_parts[2]
        ticker = re.sub(r'(/?USDT)$', '', raw_ticker, flags=re.IGNORECASE)
    else: # for everything else
        ticker = re.findall(r'\(([^)]+)\)', title)
    return ticker
    

def binance_extraction(data):
    articles = data.get('data', {}).get('catalogs', [])[0].get('articles', [])
    new_listings = []
    for article in articles:
        title = article.get('title')
        ticker = extract_ticker(title)
        timestamp_ms = article.get('releaseDate')

        release_date = datetime.fromtimestamp(timestamp_ms / 1000).strftime('%Y-%m-%d %H:%M:%S')
        new_listings.append((ticker, release_date))
    return new_listings



def bybit_extraction(data):
    articles = data.get("result", {}).get("list", [])
    new_listings = []
    for article in articles:
        if article.get("type", {}).get("key") != "new_crypto":
            continue
        ticker = extract_ticker(article.get("title", ""))
        timestamp_ms = article.get('releaseDate')



