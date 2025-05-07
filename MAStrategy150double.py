import datetime
import backtrader as bt
from tabulate import tabulate

class MAStrategy150LongShort(bt.Strategy):
    params = (
        ('sma_period', 50),
        ('stop_loss', 0.03),
        ('double_down', True),
    )

    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.p.sma_period
        )

        self.order = None
        
        self.trades: list[bt.Trade] = []
        self.exit : list[bt.Trade] = []
       
        self.equity = []
        self.max_drawdown = 0
        self.peak_equity = 0

        self.current_dir = ""

        self.idx = 0


        
    def next(self):

        # if self.data.datetime.date(0) == datetime.date(2025, 4, 20):
        #     self.close()
        #     return
        
        if self.sma[0] < self.data.close[0]:

            if self.position.size < 0:
                self.close()

            if self.p.double_down:
                self.buy(size=10)
            elif self.position.size == 0:
                self.buy(size=10)
           
        elif self.sma[0] > self.data.close[0]:

            if self.position.size > 0:
                self.close()

            if self.p.double_down:
                self.sell(size=10)
            elif self.position.size == 0:
                self.sell(size=10)

          
        current_equity = self.broker.getvalue()
        self.equity.append(current_equity)
        self.peak_equity = max(self.peak_equity, current_equity)
        drawdown = (self.peak_equity - current_equity) / self.peak_equity
        self.max_drawdown = max(self.max_drawdown, drawdown)

    
    def notify_order(self, order : bt.Order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.trades.append({
                    'ref': order.ref,
                    'date': self.data.datetime.date(0),
                    'size': order.executed.size,
                    'price': order.executed.price,
                    'pnl': order.executed.pnl,
                    'direction': "long"
                })
            
            elif order.issell():
                self.trades.append({
                    'ref': order.ref,
                    'date': self.data.datetime.date(0),
                    'size': order.executed.size,
                    'price': order.executed.price,
                    'pnl': order.executed.pnl,
                    'direction': "short"
                })
               

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            pass
        
        self.order = None
    
    def notify_trade(self, trade: bt.Trade):
 
        if trade.isclosed:
            self.exit.append(trade)
    
    
   
        
    