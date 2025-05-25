import ccxt
import pandas as pd
from datetime import datetime, timedelta

# Configure fees and slippage
TRADING_FEES = {
    'binance': 0.001,  # 0.1%
    'kucoin': 0.001,
    'bybit': 0.001
}

LATENCY_SECONDS = 15  # Time between listing signal and execution

# Simulated listing event
listing_event = {
    'symbol': 'BTC/USDT',
    'listing_exchange': 'kucoin',
    'timestamp': datetime(2024, 7, 1, 12, 0, 0)
}

# Simulated historical prices (replace with real historical snapshots)
historical_prices = {
    'kucoin': pd.DataFrame([
        {'timestamp': datetime(2024, 7, 1, 12, 0, 0), 'price': 1.00},
        {'timestamp': datetime(2024, 7, 1, 12, 0, 15), 'price': 1.05},
    ]),
    'binance': pd.DataFrame([
        {'timestamp': datetime(2024, 7, 1, 12, 0, 15), 'price': 1.10},
    ]),
    'bybit': pd.DataFrame([
        {'timestamp': datetime(2024, 7, 1, 12, 0, 15), 'price': 1.09},
    ])
}

def get_price_at(exchange_name, target_time):
    df = historical_prices[exchange_name]
    df = df[df['timestamp'] <= target_time]
    if df.empty:
        return None
    return df.iloc[-1]['price']

def simulate_arbitrage(event):
    buy_time = event['timestamp']
    sell_time = buy_time + timedelta(seconds=LATENCY_SECONDS)

    buy_exchange = event['listing_exchange']
    buy_price = get_price_at(buy_exchange, buy_time)

    if buy_price is None:
        return f"No buy price at {buy_time} on {buy_exchange}"

    print(f"BUY {event['symbol']} on {buy_exchange} at {buy_price:.4f}")

    results = []

    for sell_exchange in ['binance', 'bybit']:
        sell_price = get_price_at(sell_exchange, sell_time)
        if sell_price is None:
            continue

        fee_buy = buy_price * TRADING_FEES[buy_exchange]
        fee_sell = sell_price * TRADING_FEES[sell_exchange]

        profit = (sell_price - fee_sell) - (buy_price + fee_buy)
        profit_pct = profit / (buy_price + fee_buy) * 100

        results.append({
            'sell_exchange': sell_exchange,
            'sell_price': sell_price,
            'profit_pct': round(profit_pct, 2)
        })

    return results

# Run the backtest
results = simulate_arbitrage(listing_event)
for r in results:
    print(f"SELL on {r['sell_exchange']} at {r['sell_price']:.4f} — Profit: {r['profit_pct']}%")
