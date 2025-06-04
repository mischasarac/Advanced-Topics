import time
import csv
import asyncio
from change_listener import identify_difference
from get_orderbook import get_orderbook
from execute_trade import execute_arb, close_position
from arb_detection import detect_arb
from get_balances import BalanceManager
from close_position import close_position
from datetime import datetime, timedelta
from new_listing import ListingAggregator

LOG_FILE = "trade_log.csv"

async def wait_for_orderbook(new_ticker, timeout_seconds=28800):
    """
    Async function that checks every 5 seconds if orderbook is available for new_ticker.
    Returns True when orderbook is found, False if timeout reached.
    """
    start_time = time.time()
    
    while True:
        try:
            # Check if orderbook exists (not None)
            orderbook = get_orderbook(new_ticker[1], new_ticker[0])
            if orderbook is not None:
                print(f"✅ Orderbook found for {new_ticker[1]}/{new_ticker[0]}!")
                return True
                
        except Exception as e:
            print(f"⚠️  Error checking orderbook: {e}")
        
        # Check timeout
        if time.time() - start_time > timeout_seconds:
            print(f"⏰ Timeout reached waiting for orderbook for {new_ticker[1]}/{new_ticker[0]}")
            return False
            
        print(f"🔍 Waiting for orderbook... {new_ticker[1]}/{new_ticker[0]}")
        await asyncio.sleep(5)  # Wait 5 seconds before next check

async def run_once_async(balance_manager):
    listingAgg = ListingAggregator()
    listingAgg.gather_listings()
    new_ticker = identify_difference()

    if new_ticker is None:
        return None
    
    print(f"🆕 New ticker detected: {new_ticker}")
    
    # Wait for orderbook to become available
    orderbook_available = await wait_for_orderbook(new_ticker)
    
    if orderbook_available:
        # Orderbook is ready, proceed with arbitrage detection
        await arb_dropped_async(new_ticker, balance_manager)
    else:
        print(f"❌ Orderbook never became available for {new_ticker}")

async def arb_dropped_async(new_ticker, balance_manager):
    arb = detect_arb(new_ticker)
    if arb is None:
        # Log the detection with zero profit
        print("No arbitrage opportunity detected.")
        return
    print("Arb possible")

    # Step 5: Get current balances from BalanceManager for the relevant exchanges
    long_exchange = arb["long"][0]
    short_exchange = arb["short"][0]
    ticker = arb["ticker"]

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
        close_position(
            ticker=ticker,
            long_exchange=long_exchange,
            short_exchange=short_exchange,
            curr_trades=curr_trades,
            balance_manager=balance_manager
        )

def run_once(balance_manager):
    """Synchronous wrapper for the async function"""
    return asyncio.run(run_once_async(balance_manager))

if __name__ == "__main__":
    balance_manager = BalanceManager()  # instantiate once, holds balances across runs
    while True:
        try:
            run_once(balance_manager)
        except Exception as e:
            print(f"🔥 Error: {e}")
        except KeyboardInterrupt:
            print("🛑 Exiting gracefully.")
            break
        print(f"🛌 {datetime.now()} Sleeping 20 seconds...\n")
        time.sleep(20)