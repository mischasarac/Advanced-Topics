import time
import csv
from scan_listings import ListingAggregator
from change_listener import identify_difference
from get_orderbook import get_orderbook
from execute_trade import execute_arb, close_position
from trade_possible import detect_arb
from get_balances import BalanceManager
from datetime import datetime, timedelta


LOG_FILE = "trade_log.csv"

def run_once(balance_manager):

    # Step 1: Update listing info
    aggregator = ListingAggregator()
    aggregator.gather_listings()

    # Step 2: Detect listing change
    change = identify_difference()
    if not change:
        return
    print(f"New change: {change[0]}")
    ticker, exchanges = change
    print(f"📈 New cross-listing detected: {ticker} on {exchanges}")

    # Step 3: Get orderbooks
    orderbook = get_orderbook(ticker, exchanges)

    start_time = datetime.now()
    max_wait = timedelta(minutes=2)

    while (not orderbook) and datetime.now() - start_time < max_wait:
        orderbook = get_orderbook(ticker, exchanges)

    # Step 4: Check arbitrage opportunity
    arb = detect_arb(orderbook)
    if arb is None:
        # Log the detection with zero profit
        print("No arbitrage opportunity detected.")
        return
    print("Arb possible")

    # Step 5: Get current balances from BalanceManager for the relevant exchanges
    long_exchange = arb["long"][0]
    short_exchange = arb["short"][0]

    # Prepare balances dict with USDT amounts for each exchange from BalanceManager
    balances = {
        long_exchange: {"USDT": balance_manager.get_balance(long_exchange)["USDT"]},
        short_exchange: {"USDT": balance_manager.get_balance(short_exchange)["USDT"]},
    }

    # Step 6: Execute arbitrage (pass balance_manager to update balances internally)
    curr_trades = execute_arb(
        ticker=ticker,
        long_exchange=long_exchange,
        short_exchange=short_exchange,
        amount=balances,
        balance_manager=balance_manager
    )

    # Step 7: Wait until spread closes
    if curr_trades is not None:
        print("📉 Monitoring price convergence...")
        max_wait = timedelta(minutes=30)
        start_time = datetime.now()

        while datetime.now() - start_time < max_wait:
            time.sleep(5)
            curr_orderbook = get_orderbook(ticker, [long_exchange, short_exchange])
            long_ask = float(curr_orderbook[long_exchange]["asks"][0][0])
            short_bid = float(curr_orderbook[short_exchange]["bids"][0][0])
            if long_ask <= short_bid * 1.0005:
                print("💰 Spread closed — closing positions.")
                break
        else:
            print("⚠️ Max wait time reached — closing positions anyway.")

        # Close position and update balances accordingly
        close_position(curr_trades, balance_manager)


if __name__ == "__main__":
    balance_manager = BalanceManager()  # instantiate once, holds balances across runs
    while True:
        try:
            run_once(balance_manager)
        except Exception as e:
            print(f"🔥 Error: {e}")
        print(f"🛌 {datetime.now()} Sleeping 20 seconds...\n")
        time.sleep(20)
