import requests
from datetime import datetime
import re

def get_new_listings():
    url = "https://api.bybit.com/v5/announcements/index"
    params = {
        "locale": "en-US",
        "page": 1,
        "limit": 100
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        announcements = response.json().get("result", {}).get("list", [])

        for ann in announcements:
            if ann.get("type", {}).get("key") != "new_crypto":
                continue

            title_parts = ann.get("title", "").split()
            if len(title_parts) < 4 or title_parts[0] != "New":
                continue

            # Extract publish time and convert to readable format
            timestamp_ms = ann.get("publishTime", 0)
            publish_time = datetime.fromtimestamp(timestamp_ms / 1000)
            formatted_time = publish_time.strftime('%Y-%m-%d %H:%M:%S')

            # Extract ticker symbol
            raw_ticker = title_parts[3] if title_parts[2] == ":" else title_parts[2]

            # Remove trailing 'USDT' or '/USDT'
            ticker = re.sub(r'(/?USDT)$', '', raw_ticker, flags=re.IGNORECASE)

            print(f"Ticker: {ticker}    --->    {formatted_time}")

    except requests.RequestException as e:
        print(f"Error fetching data: {e}")

get_new_listings()
