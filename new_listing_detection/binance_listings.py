import requests
import time
import datetime

def fetch_latest_listings():
    print("Fetching latest listings...")
    url = "https://www.binance.com/bapi/composite/v1/public/cms/article/list/query"
    params = {
        "type": 1,
        "catalogId": 48,  # Catalog ID for new listings
        "pageNo": 1,
        "pageSize": 50
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        articles = data.get('data', {}).get('catalogs', [])[0].get('articles', [])
        return articles
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return []


def extract_new_listing_ticker(title: str) -> str:
    """
    Extract the ticker symbol/s from the title of the listing.
    This is a placeholder function and should be implemented based on the actual title format.
    """
    new_listings = []
    words = title.split()
    for word in words:
        if word[0] == '(' and word[-1] == ')':
            new_listings.append(word[1:-1])
    return new_listings

def monitor_new_listings():
    seen_listings = set()
    print("Monitoring for new listings...")
    while True:
        listings = fetch_latest_listings()
        for listing in listings:
            title = listing.get('title')
            release_time = listing.get('releaseDate')
            ts = datetime.datetime.fromtimestamp(release_time / 1000).strftime('%Y-%m-%d %H:%M:%S')
            tickers = extract_new_listing_ticker(title)
            for ticker in tickers:
                if ticker and ticker not in seen_listings:
                    print(f"New ticker: {ticker}    --->    Release date : {ts}")
                    seen_listings.add(ticker)
        time.sleep(60)  # Check every minute
if __name__ == "__main__":
    monitor_new_listings()