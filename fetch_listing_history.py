import ccxt
import pandas as pd
from datetime import datetime, timedelta, timezone
import time
import os

# Updated listings as a list of dicts (example snippet from your JSON)
listings = []

exchange_instances = {
    "binance": ccxt.binance(),
    "bybit": ccxt.bybit(),
    "kucoin": ccxt.kucoin()
}

symbol_formats = {
    "binance": lambda symbol: f"{symbol}/USDT",
    "bybit": lambda symbol: f"{symbol}/USDT",
    "kucoin": lambda symbol: f"{symbol}/USDT"
}

def fetch_ohlcv(exchange, symbol, start_time, duration_days=5, timeframe='1m'):
    since = int(start_time.timestamp() * 1000)
    end_time = start_time + timedelta(days=duration_days)
    all_candles = []
    while since < int(end_time.timestamp() * 1000):
        try:
            candles = exchange.fetch_ohlcv(symbol, timeframe, since)
        except Exception as e:
            print(f"[{exchange.id}] Error fetching {symbol}: {e}")
            break
        if not candles:
            break
        all_candles.extend(candles)
        since = candles[-1][0] + 1  # move just after the last fetched time
        time.sleep(exchange.rateLimit / 1000)  # respect rate limit
    df = pd.DataFrame(all_candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
    return df

def fetch_all_data(listings, save_dir='bt_data'):
    os.makedirs(save_dir, exist_ok=True)
    for entry in listings:
        symbol = entry["coin"]
        start_date_str = entry["date"]
        start_dt = datetime.strptime(start_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        for exchange_name in entry["exchanges"]:
            exchange = exchange_instances.get(exchange_name)
            if not exchange:
                print(f"Exchange {exchange_name} not supported.")
                continue
            formatted_symbol = symbol_formats[exchange_name](symbol)
            print(f"\nFetching {formatted_symbol} from {exchange_name} starting {start_dt.isoformat()}...")
            try:
                df = fetch_ohlcv(exchange, formatted_symbol, start_dt)
                if df.empty:
                    print(f"No data found for {formatted_symbol} on {exchange_name}")
                    continue
                filename = f"{save_dir}/{symbol}_{exchange_name}.csv"
                df.to_csv(filename, index=False)
                print(f"Saved to {filename}")
            except Exception as e:
                print(f"Error with {exchange_name}: {e}")

if __name__ == "__main__":
    fetch_all_data(listings)
