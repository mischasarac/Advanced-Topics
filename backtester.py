import pandas as pd
import os
from datetime import timedelta

# CONFIG
start_capital = 100
spread_entry_threshold = 0.002    # 0.2% entry
spread_exit_threshold = 0.0005    # 0.05% exit
max_holding_minutes = 200         # safety cap on how long we hold
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
    df.sort_values(by='timestamp', inplace=True)

    if df.empty:
        continue

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
            # Entry detected
            entry_time = ts
            long_price_entry = min(price1, price2)
            short_price_entry = max(price1, price2)

            # Search for exit when spread narrows
            for j in range(i + 1, len(df)):
                exit_row = df.iloc[j]
                exit_ts = exit_row['timestamp']

                if exit_ts > entry_time + timedelta(minutes=max_holding_minutes):
                    break  # Safety exit

                exit_price1 = exit_row['close_1']
                exit_price2 = exit_row['close_2']
                exit_spread = abs(exit_price1 - exit_price2) / ((exit_price1 + exit_price2) / 2)

                if exit_spread <= spread_exit_threshold:
                    # Exit condition met
                    long_price_exit = min(exit_price1, exit_price2)
                    short_price_exit = max(exit_price1, exit_price2)

                    long_size = capital / 2 / long_price_entry
                    short_size = capital / 2 / short_price_entry

                    pnl_long = long_size * (long_price_exit - long_price_entry)
                    pnl_short = short_size * (short_price_entry - short_price_exit)
                    total_pnl = pnl_long + pnl_short
                    capital += total_pnl

                    results.append({
                        "symbol": symbol,
                        "entry_time": entry_time,
                        "exit_time": exit_ts,
                        "entry_price_1": price1,
                        "entry_price_2": price2,
                        "exit_price_1": exit_price1,
                        "exit_price_2": exit_price2,
                        "pnl": total_pnl,
                        "capital": capital
                    })

                    checked = True
                    break

            if checked:
                break  # Only one trade per symbol

    if not checked:
        print(f"No arbitrage opportunity found or exit condition not met for {symbol}")

# Results
result_df = pd.DataFrame(results)
print(result_df)
print(f"\nFinal capital: ${capital:.2f}")
