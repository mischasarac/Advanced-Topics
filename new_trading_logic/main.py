import time
import csv
from change_listener import identify_difference
from get_orderbook import get_orderbook
from execute_trade import execute_arb, close_position
from arb_detection import detect_arb
from get_balances import BalanceManager
from close_position import close_position
from datetime import datetime, timedelta


LOG_FILE = "trade_log.csv"

def run_once(balance_manager):

    arb = detect_arb()
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
