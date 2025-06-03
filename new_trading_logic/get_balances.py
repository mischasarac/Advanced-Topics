import ccxt
import os
import json

class BalanceManager:
    def __init__(self):
        # Default balances in USDT
        self.balances = {
            "kucoin": {"USDT": 60.0},
            "bybit": {"USDT": 60.0},
            "binance": {"USDT": 60.0}
        }
        self.trades = 0

    def get_balance(self, exchange: str):
        """
        Get the current balance for the specified exchange.

        :param exchange: Exchange name (e.g., 'kucoin', 'bybit', 'binance')
        :return: Dictionary with USDT balance
        """
        exchange = exchange.lower()
        if exchange not in self.balances:
            raise ValueError(f"Exchange '{exchange}' not supported.")
        return self.balances[exchange]

    def set_balance(self, exchange: str, amount: float):
        """
        Set a new balance (in USDT) for the specified exchange.

        :param exchange: Exchange name (e.g., 'kucoin', 'bybit', 'binance')
        :param amount: New balance amount in USDT
        """
        exchange = exchange.lower()
        if exchange not in self.balances:
            raise ValueError(f"Exchange '{exchange}' not supported.")
        self.balances[exchange]["USDT"] = amount

    def get_all_balances(self, long_exchange: str, short_exchange: str):
        """
        Return balances for the two specified exchanges.

        :param long_exchange: Long exchange name
        :param short_exchange: Short exchange name
        :return: Dict with 'long' and 'short' balances
        """
        return {
            "long": self.get_balance(long_exchange),
            "short": self.get_balance(short_exchange)
        }
