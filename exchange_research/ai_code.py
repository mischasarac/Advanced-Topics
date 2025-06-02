#!/usr/bin/env python3
"""
Cryptocurrency Arbitrage Bot for New Listings
Monitors exchanges for new coin listings and identifies arbitrage opportunities
"""

import ccxt
import asyncio
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
import threading
from concurrent.futures import ThreadPoolExecutor
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('arbitrage_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ArbitrageOpportunity:
    """Data class for arbitrage opportunities"""
    symbol: str
    buy_exchange: str
    sell_exchange: str
    buy_price: float
    sell_price: float
    profit_percentage: float
    volume_24h: float
    timestamp: datetime

class NewListingMonitor:
    """Monitors exchanges for new coin listings"""
    
    def __init__(self, min_profit_threshold: float = 2.0):
        self.min_profit_threshold = min_profit_threshold
        self.known_symbols: Dict[str, Set[str]] = {}
        self.exchanges = self._initialize_exchanges()
        self.running = False
        
    def _initialize_exchanges(self) -> Dict[str, ccxt.Exchange]:
        """Initialize supported exchanges"""
        exchanges = {}
        
        # List of exchanges that commonly announce new listings
        exchange_configs = {
            'binance': ccxt.binance(),
            'coinbase': ccxt.coinbase(),
            'kraken': ccxt.kraken(),
            'kucoin': ccxt.kucoin(),
            'huobi': ccxt.huobi(),
            'okx': ccxt.okx(),
            'bybit': ccxt.bybit(),
            'gate': ccxt.gateio(),
            # 'mexc': ccxt.mexc(),
            'bitget': ccxt.bitget()
        }
        
        for name, exchange in exchange_configs.items():
            try:
                exchange.set_sandbox_mode(False)  # Set to True for testing
                exchange.load_markets()
                exchanges[name] = exchange
                self.known_symbols[name] = set(exchange.symbols)
                logger.info(f"Initialized {name} with {len(exchange.symbols)} symbols")
            except Exception as e:
                logger.error(f"Failed to initialize {name}: {e}")
                
        return exchanges
    
    def detect_new_listings(self) -> List[Tuple[str, str]]:
        """Detect new coin listings across exchanges"""
        new_listings = []
        
        for exchange_name, exchange in self.exchanges.items():
            try:
                exchange.load_markets()  # Refresh markets
                current_symbols = set(exchange.symbols)
                previous_symbols = self.known_symbols.get(exchange_name, set())
                
                new_symbols = current_symbols - previous_symbols
                
                if new_symbols:
                    for symbol in new_symbols:
                        new_listings.append((exchange_name, symbol))
                        logger.info(f"NEW LISTING DETECTED: {symbol} on {exchange_name}")
                    
                    self.known_symbols[exchange_name] = current_symbols
                    
            except Exception as e:
                logger.error(f"Error checking {exchange_name} for new listings: {e}")
                
        return new_listings
    
    def get_ticker_data(self, exchange_name: str, symbol: str) -> Optional[Dict]:
        """Get ticker data for a symbol on an exchange"""
        try:
            exchange = self.exchanges[exchange_name]
            ticker = exchange.fetch_ticker(symbol)
            return ticker
        except Exception as e:
            logger.debug(f"Failed to get ticker for {symbol} on {exchange_name}: {e}")
            return None
    
    def find_arbitrage_opportunities(self, symbol: str) -> List[ArbitrageOpportunity]:
        """Find arbitrage opportunities for a given symbol across exchanges"""
        opportunities = []
        prices = {}
        
        # Collect prices from all exchanges that support the symbol
        for exchange_name, exchange in self.exchanges.items():
            if symbol in exchange.symbols:
                ticker = self.get_ticker_data(exchange_name, symbol)
                if ticker and ticker.get('bid') and ticker.get('ask'):
                    prices[exchange_name] = {
                        'bid': ticker['bid'],
                        'ask': ticker['ask'],
                        'volume': ticker.get('quoteVolume', 0),
                        'timestamp': ticker.get('timestamp', time.time() * 1000)
                    }
        
        # Find arbitrage opportunities
        exchange_names = list(prices.keys())
        for i in range(len(exchange_names)):
            for j in range(i + 1, len(exchange_names)):
                buy_exchange = exchange_names[i]
                sell_exchange = exchange_names[j]
                
                buy_price = prices[buy_exchange]['ask']
                sell_price = prices[sell_exchange]['bid']
                
                # Check both directions
                for direction in [(buy_exchange, sell_exchange, buy_price, sell_price),
                                (sell_exchange, buy_exchange, prices[sell_exchange]['ask'], prices[buy_exchange]['bid'])]:
                    
                    buy_ex, sell_ex, buy_p, sell_p = direction
                    
                    if sell_p > buy_p:
                        profit_pct = ((sell_p - buy_p) / buy_p) * 100
                        
                        if profit_pct >= self.min_profit_threshold:
                            avg_volume = (prices[buy_ex]['volume'] + prices[sell_ex]['volume']) / 2
                            
                            opportunity = ArbitrageOpportunity(
                                symbol=symbol,
                                buy_exchange=buy_ex,
                                sell_exchange=sell_ex,
                                buy_price=buy_p,
                                sell_price=sell_p,
                                profit_percentage=profit_pct,
                                volume_24h=avg_volume,
                                timestamp=datetime.now()
                            )
                            opportunities.append(opportunity)
        
        return opportunities
    
    def analyze_opportunity(self, opportunity: ArbitrageOpportunity) -> Dict:
        """Analyze the viability of an arbitrage opportunity"""
        analysis = {
            'opportunity': opportunity,
            'risk_level': 'UNKNOWN',
            'execution_time_estimate': 'UNKNOWN',
            'fees_estimate': 'CALCULATE_REQUIRED',
            'recommendations': []
        }
        
        # Risk assessment based on profit percentage and volume
        if opportunity.profit_percentage > 10:
            analysis['risk_level'] = 'HIGH_REWARD_HIGH_RISK'
            analysis['recommendations'].append('Verify prices manually before execution')
        elif opportunity.profit_percentage > 5:
            analysis['risk_level'] = 'MEDIUM'
        else:
            analysis['risk_level'] = 'LOW'
        
        # Volume assessment
        if opportunity.volume_24h < 10000:  # Low volume threshold
            analysis['recommendations'].append('LOW VOLUME - Check liquidity before trading')
            
        # New listing specific warnings
        analysis['recommendations'].extend([
            'NEW LISTING - High volatility expected',
            'Monitor for price manipulation',
            'Start with small test amounts',
            'Check withdrawal/deposit status on both exchanges'
        ])
        
        return analysis
    
    def log_opportunity(self, analysis: Dict):
        """Log arbitrage opportunity with analysis"""
        opp = analysis['opportunity']
        
        log_msg = f"""
        🚨 ARBITRAGE OPPORTUNITY DETECTED 🚨
        Symbol: {opp.symbol}
        Buy: {opp.buy_exchange} @ ${opp.buy_price:.6f}
        Sell: {opp.sell_exchange} @ ${opp.sell_price:.6f}
        Profit: {opp.profit_percentage:.2f}%
        24h Volume: ${opp.volume_24h:,.2f}
        Risk Level: {analysis['risk_level']}
        Recommendations: {', '.join(analysis['recommendations'])}
        Timestamp: {opp.timestamp}
        """
        
        logger.info(log_msg)
        
        # Save to file for later analysis
        with open('arbitrage_opportunities.json', 'a') as f:
            json.dump({
                'symbol': opp.symbol,
                'buy_exchange': opp.buy_exchange,
                'sell_exchange': opp.sell_exchange,
                'buy_price': opp.buy_price,
                'sell_price': opp.sell_price,
                'profit_percentage': opp.profit_percentage,
                'volume_24h': opp.volume_24h,
                'risk_level': analysis['risk_level'],
                'timestamp': opp.timestamp.isoformat(),
                'recommendations': analysis['recommendations']
            }, f)
            f.write('\n')
    
    def monitor_new_listings(self, check_interval: int = 60):
        """Main monitoring loop for new listings and arbitrage opportunities"""
        logger.info("Starting new listing monitor...")
        self.running = True
        
        while self.running:
            try:
                # Check for new listings
                new_listings = self.detect_new_listings()
                
                # For each new listing, check for arbitrage opportunities
                for exchange_name, symbol in new_listings:
                    logger.info(f"Analyzing arbitrage opportunities for {symbol}")
                    
                    # Wait a bit for price discovery
                    time.sleep(10)
                    
                    opportunities = self.find_arbitrage_opportunities(symbol)
                    
                    for opportunity in opportunities:
                        analysis = self.analyze_opportunity(opportunity)
                        self.log_opportunity(analysis)
                
                # Also periodically check existing symbols for new arbitrage opportunities
                # (in case new exchanges start supporting existing coins)
                if len(new_listings) == 0:
                    self._check_random_symbols_for_arbitrage()
                
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                logger.info("Received interrupt signal, stopping monitor...")
                self.running = False
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(30)  # Wait before retrying
    
    def _check_random_symbols_for_arbitrage(self, sample_size: int = 10):
        """Check a random sample of symbols for arbitrage opportunities"""
        all_symbols = set()
        for exchange_symbols in self.known_symbols.values():
            all_symbols.update(exchange_symbols)
        
        # Sample a few symbols to check
        import random
        sample_symbols = random.sample(list(all_symbols), min(sample_size, len(all_symbols)))
        
        for symbol in sample_symbols:
            opportunities = self.find_arbitrage_opportunities(symbol)
            for opportunity in opportunities:
                analysis = self.analyze_opportunity(opportunity)
                if opportunity.profit_percentage >= self.min_profit_threshold:
                    self.log_opportunity(analysis)
    
    def stop(self):
        """Stop the monitoring loop"""
        self.running = False

def main():
    """Main function to run the arbitrage bot"""
    print("🤖 Crypto Arbitrage Bot for New Listings")
    print("========================================")
    
    # Configuration
    MIN_PROFIT_THRESHOLD = 0.6  # Minimum profit percentage to consider
    CHECK_INTERVAL = 60  # Seconds between checks
    
    # Initialize monitor
    monitor = NewListingMonitor(min_profit_threshold=MIN_PROFIT_THRESHOLD)
    
    try:
        # Start monitoring
        monitor.monitor_new_listings(check_interval=CHECK_INTERVAL)
    except KeyboardInterrupt:
        logger.info("Shutting down bot...")
        monitor.stop()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        monitor.stop()

if __name__ == "__main__":
    main()