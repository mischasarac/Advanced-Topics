def get_all_symbols():
    url = "https://api.bybit.com/v5/market/instruments-info"
    params = {
        "category": "spot"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        for entry in data["result"]["list"]:
            if "SOON" in entry["symbol"]:
                print(entry["symbol"])
    except requests.RequestException as e:
        print(f"Error: {e}")

get_all_symbols()
