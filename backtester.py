import pandas as pd
import os
from datetime import timedelta
from itertools import combinations

# CONFIG
start_capital = 100
spread_entry_threshold = 0.002    # 0.2% entry
spread_exit_threshold = 0.0001    # 0.05% exit
max_holding_minutes = 200
data_dir = "bt_data"

# Result tracking
results = []
capital = start_capital

# Get all files and unique symbols
files = os.listdir(data_dir)
symbols = sorted(set(f.split("_")[0] for f in files if f.endswith('.csv')))
all_exchanges = ['binance', 'bybit', 'kucoin']

for symbol in symbols:
    # Load all available exchange data for the symbol
    dfs = {}
    for ex in all_exchanges:
        filepath = f"{data_dir}/{symbol}_{ex}.csv"
        if os.path.exists(filepath):
            dfs[ex] = pd.read_csv(filepath, parse_dates=['timestamp'])

    if len(dfs) < 2:
        continue  # need at least two exchanges to arbitrage

    # Merge all dataframes on timestamp
    merged_df = None
    for ex, df in dfs.items():
        df = df[['timestamp', 'close']].rename(columns={'close': f'close_{ex}'})
        if merged_df is None:
            merged_df = df
        else:
            merged_df = pd.merge(merged_df, df, on='timestamp', how='inner')

    if merged_df is None or merged_df.empty:
        continue

    merged_df.sort_values(by='timestamp', inplace=True)
    listing_time = merged_df['timestamp'].iloc[0]
    max_check_time = listing_time + timedelta(minutes=60)
    checked = False

    for i in range(len(merged_df)):
        row = merged_df.iloc[i]
        ts = row['timestamp']
        if ts > max_check_time:
            break

        # Find the best pair with the highest spread
        best_pair = None
        max_spread = 0

        for ex1, ex2 in combinations(dfs.keys(), 2):
            price1 = row[f'close_{ex1}']
            price2 = row[f'close_{ex2}']
            spread = abs(price1 - price2) / ((price1 + price2) / 2)

            if spread > max_spread:                
                max_spread = spread
                best_pair = (ex1, price1, ex2, price2)

        if best_pair and max_spread >= spread_entry_threshold:
            entry_time = ts
            ex_long, price_long = (best_pair[0], best_pair[1]) if best_pair[1] < best_pair[3] else (best_pair[2], best_pair[3])
            ex_short, price_short = (best_pair[2], best_pair[3]) if best_pair[1] < best_pair[3] else (best_pair[0], best_pair[1])

            # Search for exit
            for j in range(i + 1, len(merged_df)):
                exit_row = merged_df.iloc[j]
                exit_ts = exit_row['timestamp']

                if exit_ts > entry_time + timedelta(minutes=max_holding_minutes):
                    break

                if f'close_{ex_long}' not in exit_row or f'close_{ex_short}' not in exit_row:
                    continue  # Skip if missing prices

                long_exit = exit_row[f'close_{ex_long}']
                short_exit = exit_row[f'close_{ex_short}']

                exit_spread = abs(long_exit - short_exit) / ((long_exit + short_exit) / 2)

                if exit_spread <= spread_exit_threshold:
                    # Calculate PnL
                    long_size = capital / 2 / price_long
                    short_size = capital / 2 / price_short

                    pnl_long = long_size * (long_exit - price_long)
                    pnl_short = short_size * (price_short - short_exit)
                    total_pnl = pnl_long + pnl_short
                    capital += total_pnl

                    results.append({
                        "symbol": symbol,
                        "entry_time": entry_time,
                        "exit_time": exit_ts,
                        "entry_exchange_long": ex_long,
                        "entry_exchange_short": ex_short,
                        "entry_price_long": price_long,
                        "entry_price_short": price_short,
                        "exit_price_long": long_exit,
                        "exit_price_short": short_exit,
                        "pnl": total_pnl,
                        "capital": capital
                    })

                    checked = True
                    break

            if checked:
                break

    if not checked:
        print(f"No arbitrage opportunity found or exit condition not met for {symbol}")

# Results
result_df = pd.DataFrame(results)
print(result_df)
print(f"\nFinal capital: ${capital:.2f}")
