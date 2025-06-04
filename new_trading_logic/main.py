import time
import asyncio
from change_listener import identify_difference
from get_orderbook import get_orderbook
from execute_trade import execute_arb
from arb_detection import detect_arb
from get_balances import BalanceManager
from close_position import close_position
from datetime import datetime
from new_listing import ListingAggregator

LOG_FILE = "trade_log.csv"

async def wait_for_orderbook(new_ticker, timeout_seconds=28800):
    start_time = time.time()
    while True:
        try:
            orderbook = get_orderbook(new_ticker[1], new_ticker[0])
            if orderbook is not None:
                print(f"✅ Orderbook found for {new_ticker[1]}/{new_ticker[0]}!")
                return True
        except Exception as e:
            print(f"⚠️  Error checking orderbook: {e}")
        if time.time() - start_time > timeout_seconds:
            print(f"⏰ Timeout reached waiting for orderbook for {new_ticker[1]}/{new_ticker[0]}")
            return False
        print(f"🔍 Waiting for orderbook... {new_ticker[1]}/{new_ticker[0]}")
        await asyncio.sleep(5)

async def arb_dropped_async(new_ticker, balance_manager):
    arb = detect_arb(new_ticker)
    if arb is None:
        print("No arbitrage opportunity detected.")
        return

    print("✅ Arbitrage opportunity detected!")

    long_exchange = arb["long"][0]
    short_exchange = arb["short"][0]
    ticker = arb["ticker"]

    balances = {
        long_exchange: {"USDT": balance_manager.get_balance(long_exchange)["USDT"]},
        short_exchange: {"USDT": balance_manager.get_balance(short_exchange)["USDT"]},
    }

    curr_trades = execute_arb(
        ticker=ticker,
        long_exchange=long_exchange,
        short_exchange=short_exchange,
        amount=balances,
        balance_manager=balance_manager
    )

    if curr_trades is not None:
        close_position(
            ticker=ticker,
            long_exchange=long_exchange,
            short_exchange=short_exchange,
            curr_trades=curr_trades,
            balance_manager=balance_manager
        )

async def monitor_listing(new_ticker, balance_manager):
    orderbook_available = await wait_for_orderbook(new_ticker)
    if orderbook_available:
        await arb_dropped_async(new_ticker, balance_manager)
    else:
        print(f"❌ Orderbook never became available for {new_ticker}")

async def listing_detection_loop(balance_manager):
    seen_tickers = set()
    while True:
        try:
            listingAgg = ListingAggregator()
            listingAgg.gather_listings()
            new_ticker = identify_difference()
            if new_ticker and tuple(new_ticker) not in seen_tickers:
                seen_tickers.add(tuple(new_ticker))
                print(f"🆕 Detected: {new_ticker} — launching monitor task.")
                asyncio.create_task(monitor_listing(new_ticker, balance_manager))
        except Exception as e:
            print(f"🔥 Error: {e}")
        print(f"Sleeping another 20 seconds : {datetime.now()}")
        await asyncio.sleep(20)

if __name__ == "__main__":
    balance_manager = BalanceManager()
    try:
        asyncio.run(listing_detection_loop(balance_manager))
    except KeyboardInterrupt:
        print("🛑 Exiting gracefully.")
