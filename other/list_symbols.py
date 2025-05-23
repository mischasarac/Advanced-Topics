import requests

url = "https://api.binance.com/api/v3/exchangeInfo"
response = requests.get(url)
data = response.json()
symbols = [s['symbol'] for s in data['symbols']]
print(symbols)
