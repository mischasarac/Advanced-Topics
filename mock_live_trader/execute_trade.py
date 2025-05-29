import csv
import os
from get_orderbook import get_orderbook
from get_balances import BalanceManager

LOG_FILE = "trade_log.csv"

# Helper to initialize CSV with headers if not exists
def init_log_file():
    if not os.path.isfile(LOG_FILE):
        with open(LOG_FILE, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp",
                "action",           # "execute_arb" or "close_position"
                "exchange",
                "ticker",
                "trade_type",       # "long" or "short"
                "trade_amount",
                "trade_price",
                "balance_after",
                "pnl"               # only for close_position, else empty
            ])

# Write a trade record to CSV
def log_trade(action, exchange, ticker, trade_type, trade_amount, trade_price, balance_after, pnl=""):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, action, exchange, ticker, trade_type, f"{trade_amount:.6f}", f"{trade_price:.2f}", f"{balance_after:.2f}", f"{pnl}"])

# Execute long or short based on input parameters
def execute_arb(ticker: str, long_exchange: str, short_exchange: str, amount: dict, balance_manager):
    init_log_file()

    # Get current balances from dict input
    long_amount = amount.get(long_exchange, {}).get("USDT", 0)
    short_amount = amount.get(short_exchange, {}).get("USDT", 0)

    max_trade_amount = min(long_amount, short_amount)
    if max_trade_amount <= 0:
        print("No valid trade amount provided.")
        return
    
    curr_orderbook = get_orderbook(ticker, [long_exchange, short_exchange])
    if not curr_orderbook:
        print("Failed to retrieve orderbook.")
        return
    long_price = curr_orderbook[long_exchange]['asks'][0][0] if long_exchange in curr_orderbook else None
    short_price = curr_orderbook[short_exchange]['bids'][0][0] if short_exchange in curr_orderbook else None
    if long_price is None or short_price is None:
        print("Failed to retrieve prices for exchanges.")
        return
    
    # Calculate amount to trade based on the best price (crypto amount)
    long_trade_amount = max_trade_amount / long_price
    short_trade_amount = max_trade_amount / short_price

    # Update balances: subtract USDT spent for entering positions
    new_long_balance = long_amount - max_trade_amount
    new_short_balance = short_amount - max_trade_amount
    balance_manager.set_balance(long_exchange, new_long_balance)
    balance_manager.set_balance(short_exchange, new_short_balance)

    print(f"Executed arb: Long {long_trade_amount:.6f} at {long_price:.2f} on {long_exchange}, balance now {new_long_balance:.2f} USDT")
    print(f"Executed arb: Short {short_trade_amount:.6f} at {short_price:.2f} on {short_exchange}, balance now {new_short_balance:.2f} USDT")

    # Log trades to CSV
    log_trade("execute_arb", long_exchange, ticker, "long", long_trade_amount, long_price, new_long_balance)
    log_trade("execute_arb", short_exchange, ticker, "short", short_trade_amount, short_price, new_short_balance)

    return {
        "long": {
            "exchange": long_exchange,
            "ticker": ticker,
            "amount": long_trade_amount,
            "price": long_price
        },
        "short": {
            "exchange": short_exchange,
            "ticker": ticker,
            "amount": short_trade_amount,
            "price": short_price
        }
    }
    
def close_position(position: dict, balance_manager):
    init_log_file()
    trade_cost = 0.001
    long_trade = position.get('long', {})
    short_trade = position.get('short', {})
    
    if not long_trade or not short_trade:
        print("Invalid position format: missing long or short trade information.")
        return
    
    curr_orderbook = get_orderbook(long_trade['ticker'], [long_trade['exchange'], short_trade['exchange']])
    if not curr_orderbook:
        print("Failed to retrieve orderbook.")
        return
    
    long_close_price = curr_orderbook[long_trade['exchange']]['bids'][0][0] if long_trade['exchange'] in curr_orderbook else None
    short_close_price = curr_orderbook[short_trade['exchange']]['asks'][0][0] if short_trade['exchange'] in curr_orderbook else None
    if long_close_price is None or short_close_price is None:
        print("Failed to retrieve prices for exchanges.")
        return
    
    long_entry_price = long_trade['price']
    short_entry_price = short_trade['price']
    long_amount = long_trade['amount']
    short_amount = short_trade['amount']
    
    long_pnl = (long_close_price - long_entry_price) * long_amount
    short_pnl = (short_entry_price - short_close_price) * short_amount
    total_pnl = long_pnl + short_pnl

    # Update balances by adding back initial amount plus PnL
    old_long_balance = balance_manager.get_balance(long_trade['exchange'])["USDT"]
    old_short_balance = balance_manager.get_balance(short_trade['exchange'])["USDT"]

    new_long_balance = old_long_balance + (long_entry_price * long_amount) + long_pnl
    new_long_balance -= new_long_balance * trade_cost
    new_short_balance = old_short_balance + (short_entry_price * short_amount) + short_pnl
    new_short_balance -= new_short_balance * trade_cost

    balance_manager.set_balance(long_trade['exchange'], new_long_balance)
    balance_manager.set_balance(short_trade['exchange'], new_short_balance)

    print(f"Closing long on {long_trade['exchange']} at {long_close_price:.2f} (entry: {long_entry_price:.2f}) | Amount: {long_amount:.6f} | PnL: {long_pnl:.2f} | New balance: {new_long_balance:.2f} USDT")
    print(f"Closing short on {short_trade['exchange']} at {short_close_price:.2f} (entry: {short_entry_price:.2f}) | Amount: {short_amount:.6f} | PnL: {short_pnl:.2f} | New balance: {new_short_balance:.2f} USDT")
    print(f"Total PnL: {total_pnl:.2f}")

    # Log closing trades to CSV
    log_trade("close_position", long_trade['exchange'], long_trade['ticker'], "long", long_amount, long_close_price, new_long_balance, f"{long_pnl:.2f}")
    log_trade("close_position", short_trade['exchange'], short_trade['ticker'], "short", short_amount, short_close_price, new_short_balance, f"{short_pnl:.2f}")
