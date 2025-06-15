from datetime import datetime, timedelta
import time
from get_orderbook import get_orderbook
from get_balances import BalanceManager
from execute_trade import close_trade



def close_position(ticker : str, long_exchange : str, short_exchange : str, curr_trades, balance_manager):
    print("📉 Monitoring price convergence...")
    max_wait = timedelta(minutes=30)
    start_time = datetime.now()

    while datetime.now() - start_time < max_wait:
        time.sleep(5)
        long_orderbook = get_orderbook(ticker, long_exchange)
        short_orderbook = get_orderbook(ticker, short_exchange)
        if long_orderbook is None or short_orderbook is None:
            print("Error getting orderbook")
            continue
        long_ask = float(long_orderbook["asks"][0][0])
        short_bid = float(short_orderbook["bids"][0][0])
        if long_ask <= short_bid * 1.0005:
            print("💰 Spread closed — closing positions.")
            break
    else:
        print("⚠️ Max wait time reached — closing positions anyway.")

    # Close position and update balances accordingly
    close_trade(curr_trades, balance_manager)