import requests
import json
import re
from datetime import datetime, timedelta, UTC
from collections import defaultdict

import re

def extract_coin_symbol(title: str) -> str | None:
    # Try to extract from the leading "SYMBOL : " format
    leading_match = re.match(r'^(\S+) :', title)
    if leading_match:
        symbol = leading_match.group(1)
        if symbol != "None":
            return symbol
    
    # Try to find a symbol inside parentheses, usually uppercase letters and digits
    # Match something like (SYMBOL) with letters, digits, maybe dashes/underscores
    paren_match = re.findall(r'\(([\w\d\-]+)\)', title)
    if paren_match:
        # Return first match
        return paren_match[0]
    
    # Sometimes the symbol is mentioned without parentheses but ends with USDT or similar, 
    # e.g., "USDⓈ-Margined SXTUSDT Perpetual Contract"
    # We can try to extract those symbols by searching for words ending with "USDT" or "BTC", etc.
    usdt_match = re.findall(r'\b([A-Z0-9]{2,})USDT\b', title)
    if usdt_match:
        return usdt_match[0]
    
    # No symbol found
    return None


def fetch_binance_listings():
    print("Fetching Binance listings...")
    url = "https://www.binance.com/bapi/composite/v1/public/cms/article/list/query"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.binance.com/en/support/announcement/c-48",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "application/json, text/plain, */*"
    }
    listings = []
    max_pages = 5

    for page in range(1, max_pages + 1):
        params = {
            "type": 1,
            "catalogId": 48,
            "pageNo": page,
            "pageSize": 20
        }
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            articles = data.get('data', {}).get('catalogs', [])[0].get('articles', [])
            if not articles:
                break
            for article in articles:
                release_timestamp = article.get("releaseDate")
                release_date = (
                    datetime.fromtimestamp(release_timestamp / 1000, UTC).strftime('%Y-%m-%d, %H:%M:%S')
                    if release_timestamp else ""
                )
                listings.append({
                    "exchange": "binance",
                    "title": article.get("title", ""),
                    "date": release_date
                })
        except requests.RequestException as e:
            print(f"Error fetching Binance listings: {e}")
            break
    return listings

def fetch_bybit_listings():
    print("Fetching Bybit listings...")
    url = "https://api.bybit.com/v5/announcements/index"
    params = {"locale": "en-US", "page": 1, "limit": 100}
    listings = []
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        articles = data.get("result", {}).get("list", [])
        for article in articles:
            if article.get("type", {}).get("key") == "new_crypto":
                release_timestamp = article.get("createdAt")
                release_date = (
                    datetime.fromtimestamp(release_timestamp / 1000, UTC).strftime('%Y-%m-%d, %H:%M:%S')
                    if release_timestamp else ""
                )
                listings.append({
                    "exchange": "bybit",
                    "title": article.get("title", ""),
                    "date": release_date
                })
    except requests.RequestException as e:
        print(f"Error fetching Bybit listings: {e}")
    return listings

def fetch_kucoin_listings():
    print("Fetching KuCoin listings...")
    url = "https://api.kucoin.com/api/v3/announcements"
    params = {"annType": "new-listings", "lang": "en_US", "pageSize": 100}
    listings = []
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        articles = data.get("data", {}).get("items", [])
        for article in articles:
            release_timestamp = article.get("cTime")
            release_date = (
                datetime.fromtimestamp(release_timestamp / 1000, UTC).strftime('%Y-%m-%d, %H:%M:%S')
                if release_timestamp else ""
            )
            listings.append({
                "exchange": "kucoin",
                "title": article.get("annTitle", ""),
                "date": release_date
            })
    except requests.RequestException as e:
        print(f"Error fetching KuCoin listings: {e}")
    return listings

def aggregate_listings():
    print("Aggregating listings...")
    listings = fetch_binance_listings() + fetch_bybit_listings() + fetch_kucoin_listings()

    one_year_ago = datetime.now(UTC) - timedelta(days=365)
    coin_dict = defaultdict(lambda: {"date": "", "exchanges": set()})

    for listing in listings:
        title = listing["title"]
        symbol = extract_coin_symbol(title)
        # print(f"{symbol} : {title}")
        if not symbol:
            continue
        date = listing["date"]
        if not date:
            continue
        date_dt = datetime.strptime(date, "%Y-%m-%d, %H:%M:%S").replace(tzinfo=UTC)
        if date_dt < one_year_ago:
            continue

        current = coin_dict[symbol]
        if not current["date"] or date_dt > datetime.strptime(current["date"], "%Y-%m-%d, %H:%M:%S").replace(tzinfo=UTC):
            print(date)
            current["date"] = date
        current["exchanges"].add(listing["exchange"])

    # Prepare final list
    final = []
    for coin, data in coin_dict.items():
        if len(data["exchanges"]) < 2: continue
        final.append({
            "coin": coin,
            "date": data["date"],
            "exchanges": sorted(data["exchanges"])
        })

    # Save to JSON
    output_path = "/home/mischa/topics/Advanced-Topics/recent_listings.json"
    with open(output_path, "w") as f:
        json.dump(final, f, indent=2)
    print(f"Saved {len(final)} recent aggregated listings to {output_path}")

if __name__ == "__main__":
    aggregate_listings()
