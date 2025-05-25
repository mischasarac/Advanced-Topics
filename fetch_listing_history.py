import ccxt
import pandas as pd
from datetime import datetime, timedelta, timezone
import time



def fetch_ohlcv(exchange, symbol, start_time, duration_days=1, timeframe='1m'):
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
        time.sleep(exchange.rateLimit / 1000)  # to respect API limits

    df = pd.DataFrame(all_candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
    return df


def fetch_all_exchanges(symbol_base, start_time):
    exchanges = {
        'kucoin': ccxt.kucoin(),
        'binance': ccxt.binance(),
        'bybit': ccxt.bybit()
    }
    # For appending to end of ticker in request
    ticker_append = {
        "kucoin" : "/USDT",
        "bybit" : "USDT",
        "binance" : "USDT"
    }

    for name, exchange in exchanges.items():
        symbol = symbol_base + ticker_append[name]
        print(f"\nFetching {symbol} from {name}...")
        try:
            df = fetch_ohlcv(exchange, symbol, start_time)
            if df.empty:
                print(f"No data found for {symbol} on {name}")
                continue

            filename = f"{symbol_base.replace('/', '-')}_{name}.csv"
            df.to_csv(filename, index=False)
            print(f"Saved to {filename}")
        except Exception as e:
            print(f"Error with {name}: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fetch 5-day price history after listing")
    parser.add_argument("--symbol", type=str, help="Symbol like 'XYZ/USDT'")
    parser.add_argument("--start_date", type=str, help="Listing start date in YYYY-MM-DD format")

    args = parser.parse_args()
    start_dt = datetime.strptime(args.start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)


    fetch_all_exchanges(args.symbol, start_dt)
