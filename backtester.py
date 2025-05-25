import pandas as pd
import os
from datetime import timedelta

# CONFIG
start_capital = 100
spread_entry_threshold = 0.002  # 0.2%
spread_exit_threshold = 0.0005   # 0.1%
holding_period_minutes = 200     # fixed holding time
data_dir = "bt_data"              # directory with your CSVs

# Result tracking
results = []
capital = start_capital

# Get all listed tokens (with both kucoin and bybit data)
files = os.listdir(data_dir)
symbols = sorted(set(f.split("_")[0] for f in files if f.endswith('.csv')))
exchanges = ['kucoin', 'bybit']

for symbol in symbols:
    kucoin_file = f"{data_dir}/{symbol}_kucoin.csv"
    bybit_file = f"{data_dir}/{symbol}_bybit.csv"

    if not os.path.exists(kucoin_file) or not os.path.exists(bybit_file):
        continue

    df1 = pd.read_csv(kucoin_file, parse_dates=['timestamp'])
    df2 = pd.read_csv(bybit_file, parse_dates=['timestamp'])

    df = pd.merge(df1, df2, on='timestamp', suffixes=('_1', '_2'))

    if df.empty:
        continue

    # Check for arbitrage opportunities in the first 30 minutes
    listing_time = df['timestamp'].iloc[0]
    max_check_time = listing_time + timedelta(minutes=30)
    checked = False

    for i in range(len(df)):
        row = df.iloc[i]
        ts = row['timestamp']

        if ts > max_check_time:
            break

        price1 = row['close_1']
        price2 = row['close_2']
        spread = abs(price1 - price2) / ((price1 + price2) / 2)

        if spread >= spread_entry_threshold:
            # Entry
            entry_time = ts
            exit_time = entry_time + timedelta(minutes=holding_period_minutes)

            # Find exit index
            future_df = df[df['timestamp'] >= exit_time]
            if future_df.empty:
                break

            exit_row = future_df.iloc[0]

            # Simulate one long and one short
            long_price_entry = min(price1, price2)
            short_price_entry = max(price1, price2)

            long_price_exit = min(exit_row['close_1'], exit_row['close_2'])
            short_price_exit = max(exit_row['close_1'], exit_row['close_2'])

            # Assume we allocate half capital to long and half to short
            long_size = capital / 2 / long_price_entry
            short_size = capital / 2 / short_price_entry

            pnl_long = long_size * (long_price_exit - long_price_entry)
            pnl_short = short_size * (short_price_entry - short_price_exit)
            total_pnl = pnl_long + pnl_short
            capital += total_pnl

            results.append({
                "symbol": symbol,
                "entry_time": entry_time,
                "exit_time": exit_row['timestamp'],
                "entry_price_1": price1,
                "entry_price_2": price2,
                "exit_price_1": exit_row['close_1'],
                "exit_price_2": exit_row['close_2'],
                "pnl": total_pnl,
                "capital": capital
            })

            checked = True
            break

    if not checked:
        print(f"No arbitrage opportunity found for {symbol} in first 30 minutes")

# Results
result_df = pd.DataFrame(results)
print(result_df)
print(f"\nFinal capital: ${capital:.2f}")
