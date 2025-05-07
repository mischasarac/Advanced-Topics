from binance.client import Client
import pandas as pd
import time

# === CONFIG ===
api_key = ''
api_secret = ''
client = Client(api_key, api_secret)

# === SYMBOLS ===
symbols_raw = '''
BTC/USDT BTC/USDC BTC/FDUSD ETH/USDT ETH/USDC ETH/FDUSD SOL/USDT SOL/USDC SOL/FDUSD
XRP/USDT XRP/USDC XRP/FDUSD TRUMP/USDT TRUMP/USDC TRUMP/FDUSD DOGE/USDT DOGE/USDC DOGE/FDUSD
SHIB/USDT SHIB/USDC SHIB/FDUSD PEPE/USDT PEPE/USDC PEPE/FDUSD BROCCOLI714/USDT BROCCOLI714/USDC
TUT/USDT TUT/USDC LINK/USDT LINK/USDC LINK/FDUSD UNI/USDT UNI/USDC UNI/FDUSD XTZ/USDT XTZ/USDC
CAKE/USDT CAKE/USDC SUSHI/USDT LQTY/USDT FUN/USDT USDC/USDT FDUSD/USDT FDUSD/USDC BNB/USDT
BNB/USDC BNB/FDUSD XRP/BNB BNB/ETH SOL/BNB ETH/BTC XRP/BTC SOL/BTC SOL/ETH SHIB/DOGE LINK/BNB
LINK/BTC LINK/ETH UNI/BTC UNI/ETH CAKE/BNB CAKE/BTC SUSHI/BTC
'''

symbols = [s.replace('/', '') for s in symbols_raw.strip().split()]

# === INTERVALS ===
intervals = [
    # Client.KLINE_INTERVAL_1SECOND,
    Client.KLINE_INTERVAL_1MINUTE,
    Client.KLINE_INTERVAL_5MINUTE,
    Client.KLINE_INTERVAL_15MINUTE,
    Client.KLINE_INTERVAL_1HOUR,
    Client.KLINE_INTERVAL_4HOUR,
    Client.KLINE_INTERVAL_1DAY,
]

# === TIME RANGE ===
start_str = "1 Jan, 2025"

# === LOOP THROUGH SYMBOLS AND INTERVALS ===
for symbol in symbols:
    for interval in intervals:
        try:
            print(f"\n📥 Fetching {symbol} | Interval: {interval}")
            klines = client.get_historical_klines(symbol, interval, start_str)

            if not klines:
                print(f"⚠️ No data for {symbol} at interval {interval}")
                continue

            # Convert to DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'num_trades',
                'taker_buy_base_vol', 'taker_buy_quote_vol', 'ignore'
            ])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')

            # Save to CSV
            safe_interval = interval.replace(" ", "_")
            filename = f"bt_data/{symbol}_{safe_interval}.csv"
            df.to_csv(filename, index=False)
            print(f"✅ Saved {len(df)} rows to {filename}")

            # Avoid rate limit
            time.sleep(0.5)

        except Exception as e:
            print(f"❌ Error for {symbol} at {interval}: {e}")
            time.sleep(2)