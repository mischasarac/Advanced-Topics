import requests
from datetime import datetime
import re

def fetch_kucoin_new_listings():
    url = "https://api.kucoin.com/api/v3/announcements"
    params = {
        "annType": "new-listings",
        "lang": "en_US",
        "pageSize": 10
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("code") == "200000":
            items = data["data"]["items"]
            print("🔔 Latest KuCoin New Listings:")
            for item in items:
                title = item.get("annTitle", "")
                timestamp = item.get("cTime", 0)
                # Convert timestamp from milliseconds to seconds
                date = datetime.utcfromtimestamp(timestamp / 1000).strftime('%Y-%m-%d')
                # Extract ticker symbols using regex
                tickers = re.findall(r'\(([^)]+)\)', title)
                if tickers:
                    for ticker in tickers:
                        print(f"- {ticker.upper()} listed on {date}")
                else:
                    print(f"- No ticker found in title: '{title}'")
        else:
            print(f"Unexpected response code: {data.get('code')}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching KuCoin listings: {e}")

if __name__ == "__main__":
    fetch_kucoin_new_listings()
