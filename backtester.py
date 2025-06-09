import pandas as pd
import os
from datetime import timedelta
from itertools import combinations

# CONFIG
start_capital = 100
spread_entry_threshold = 0.002
spread_exit_threshold = 0.00005
max_holding_minutes = 200
data_dir = "bt_data"

# Trading constraints
ENTRY_DELAY = 60          # seconds
EXIT_DELAY = 10           # seconds
FEE_RATE = 0.001         # 0.1% per side

# Result tracking
results = []
capital = start_capital

# Load symbols
files = os.listdir(data_dir)
symbols = sorted(set(f.split("_")[0] for f in files if f.endswith('.csv')))
all_exchanges = ['binance', 'bybit', 'kucoin']

banned = {
    # "SIGN",
    # "DOOD"
}


for symbol in symbols:
    # Load exchange data
    dfs = {}
    for ex in all_exchanges:
        path = f"{data_dir}/{symbol}_{ex}.csv"
        if os.path.exists(path) and symbol not in banned:
            dfs[ex] = pd.read_csv(path, parse_dates=['timestamp'])

    if len(dfs) < 2:
        continue

    # Merge dataframes on timestamp
    merged_df = None
    for ex, df in dfs.items():
        df = df[['timestamp', 'close']].rename(columns={'close': f'close_{ex}'})
        merged_df = df if merged_df is None else pd.merge(merged_df, df, on='timestamp', how='inner')

    if merged_df is None or merged_df.empty:
        continue

    merged_df.sort_values(by='timestamp', inplace=True)
    timestamps = merged_df['timestamp']
    time_interval = (timestamps.iloc[1] - timestamps.iloc[0]).total_seconds()
    delay_entry_steps = int(ENTRY_DELAY / time_interval)
    delay_exit_steps = int(EXIT_DELAY / time_interval)

    listing_time = merged_df['timestamp'].iloc[0]
    max_check_time = listing_time + timedelta(minutes=30)
    checked = False

    for i in range(len(merged_df)):
        if merged_df['timestamp'].iloc[i] > max_check_time:
            break

        row = merged_df.iloc[i]
        best_pair = None
        max_spread = 0

        for ex1, ex2 in combinations(dfs.keys(), 2):
            price1 = row[f'close_{ex1}']
            price2 = row[f'close_{ex2}']
            spread = abs(price1 - price2) / ((price1 + price2) / 2)
            if spread - (FEE_RATE * 4 + spread_exit_threshold) > max_spread:
                max_spread = spread
                best_pair = (ex1, price1, ex2, price2)

        if best_pair and max_spread >= spread_entry_threshold:
            entry_time = row['timestamp']

            if i + delay_entry_steps >= len(merged_df):
                break

            delayed_entry_row = merged_df.iloc[i + delay_entry_steps]
            ex_long, price_long = (best_pair[0], best_pair[1]) if best_pair[1] < best_pair[3] else (best_pair[2], best_pair[3])
            ex_short, price_short = (best_pair[2], best_pair[3]) if best_pair[1] < best_pair[3] else (best_pair[0], best_pair[1])
            price_long_exec = delayed_entry_row[f'close_{ex_long}']
            price_short_exec = delayed_entry_row[f'close_{ex_short}']
            entry_exec_time = delayed_entry_row['timestamp']

            # Search for exit
            for j in range(i + 1, len(merged_df)):
                exit_row = merged_df.iloc[j]
                if exit_row['timestamp'] > entry_exec_time + timedelta(minutes=max_holding_minutes):
                    break

                if j + delay_exit_steps >= len(merged_df):
                    break

                delayed_exit_row = merged_df.iloc[j + delay_exit_steps]
                long_exit = delayed_exit_row[f'close_{ex_long}']
                short_exit = delayed_exit_row[f'close_{ex_short}']
                exit_spread = abs(long_exit - short_exit) / ((long_exit + short_exit) / 2)

                if exit_spread <= spread_exit_threshold:
                    long_size = capital / 2 / price_long_exec
                    short_size = capital / 2 / price_short_exec

                    pnl_long = long_size * (long_exit - price_long_exec)
                    pnl_short = short_size * (price_short_exec - short_exit)

                    notional_long = long_size * price_long_exec
                    notional_short = short_size * price_short_exec
                    total_fees = (notional_long + notional_short) * FEE_RATE * 2  # entry + exit

                    total_pnl = pnl_long + pnl_short - total_fees
                    percent_profit = total_pnl / capital
                    capital += total_pnl

                    results.append({
                        "symbol": symbol,
                        # "entry_time": entry_time,
                        "entry_exec_time": entry_exec_time,
                        # "exit_time": exit_row['timestamp'],
                        # "exit_exec_time": delayed_exit_row['timestamp'],
                        # "entry_exchange_long": ex_long,
                        # "entry_exchange_short": ex_short,
                        "entry_price_long": price_long_exec,
                        "entry_price_short": price_short_exec,
                        "exit_price_long": long_exit,
                        "exit_price_short": short_exit,
                        # "pnl": total_pnl,
                        "pnl %" : percent_profit * 100,
                        # "fees": total_fees,
                        # "capital": capital
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
