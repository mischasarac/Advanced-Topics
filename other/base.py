import backtrader as bt
import pandas as pd
import backtrader.analyzers as btanalyzers
from MAStrategy150double import MAStrategy150LongShort  # assuming strategy is in this file
from tabulate import tabulate
import matplotlib.pyplot as plt

# --- 1. Load your data ---
# Example: load from CSV
data = pd.read_csv('./bt_data/XRPUSDT_1d.csv', parse_dates=True, index_col='timestamp')

# remove the last row
data = data[:-1]

# Make sure the index is datetime and columns include: open, high, low, close, volume
data_feed = bt.feeds.PandasData(dataname=data)

# --- 2. Setup Cerebro ---
cerebro : bt.Cerebro = bt.Cerebro()

# Add analyzers BEFORE running cerebro
cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='sharpe', timeframe=bt.TimeFrame.Days, compression=1)
cerebro.addanalyzer(btanalyzers.TradeAnalyzer, _name='trades')
cerebro.addanalyzer(btanalyzers.Returns, _name='returns')
cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
cerebro.addanalyzer(btanalyzers.SharpeRatio_A, _name='sharpe_a', timeframe=bt.TimeFrame.Days, compression=1)
   

cerebro.addstrategy(MAStrategy150LongShort)

# Optional: set initial capital
cerebro.broker.set_cash(1000)

# Optional: set commission'
comission = 0.001
cerebro.broker.setcommission(commission=comission)  # 0.1% commission

# Optional: set slippage
# slippage = 0.01
# cerebro.broker.set_slippage_perc(perc=slippage)  # percentage slippage

double_down = True

# Add data feed
cerebro.adddata(data_feed)

# --- 3. Run backtest ---
# Run and get strategy instance
results = cerebro.run()
strat = results[0]

print("Trades:")

trades = []

previous_pos = strat.trades[0]['direction']
j = 0

for i in range(len(strat.trades)):

    if double_down:
        current_pos = strat.trades[i]['direction']

        if current_pos == previous_pos:
            trades.append(strat.trades[i])
            trades[-1]['pnl $'] = None
        else:
            while j < min(i,len(trades)):
                entry_price = trades[j]['price']
                size = trades[j]['size']
                exit_price = strat.trades[i]['price']
                direction = trades[j]['direction']

                if direction == 'long':
                    gross_pnl = (exit_price - entry_price) * size
                else:
                    gross_pnl = (entry_price - exit_price) * abs(size)
                
                commission_cost = (entry_price + exit_price) * abs(size) * comission

                net_pnl = gross_pnl - commission_cost
            
                trades[j]['pnl $'] = net_pnl
                trades[j]['pnl %'] = (trades[j]['pnl $'] / (entry_price * abs(size))) * 100
                trades[j]['exit_price'] = strat.trades[i]['price']
                trades[j]['exit_date'] = strat.trades[i]['date']
                trades[j]['duration'] = strat.trades[i]['date'] - strat.trades[j]['date']
                j += 1
        
        previous_pos = current_pos

    else:
        if i%2 == 0:
            trades.append(strat.trades[i])
            trades[-1]['pnl $'] = None
        else:
            entry_price = trades[j]['price']
            size = trades[j]['size']
            exit_price = strat.trades[i]['price']
            direction = trades[j]['direction']

            if direction == 'long':
                gross_pnl = (exit_price - entry_price) * size
            else:
                gross_pnl = (entry_price - exit_price) * abs(size)
            
            commission_cost = (entry_price + exit_price) * abs(size) * comission

            net_pnl = gross_pnl - commission_cost
        
            trades[j]['pnl $'] = net_pnl
            trades[j]['pnl %'] = (trades[j]['pnl $'] / (entry_price * abs(size))) * 100
            trades[j]['exit_price'] = strat.trades[i]['price']
            trades[j]['exit_date'] = strat.trades[i]['date']
            trades[j]['duration'] = strat.trades[i]['date'] - strat.trades[j]['date']
            j += 1

# unrealized_pnl = 0

# # Calculate unrealized PnL for open trades
# for i in range(j, len(trades)):
#     entry_price = trades[i]['price']
#     size = trades[i]['size']
#     exit_price = 2.08550000
#     direction = trades[i]['direction']

#     # priced without commission for exits
#     commission_cost = (entry_price) * abs(size) * comission

#     if direction == 'long':
#         unrealized_pnl += (exit_price - entry_price) * size - commission_cost
       
#     else:
#         unrealized_pnl += (entry_price - exit_price) * abs(size) - commission_cost
     
    
# remove 'ref' and 'pnl' columns
for trade in trades:
    trade.pop('ref', None)
    trade.pop('pnl', None)

# Plotting coin history
cerebro.plot(style='candlestick', plotname='XRP/USDT', plotvolume=False, plotbartext=False, plotymargin=0.1)
# Save coin hisory plot to file
plt.savefig('coin_history.png')
# plotting pnl
plt.figure(figsize=(10, 5))
plt.plot([trade['date'] for trade in trades], [trade['pnl $'] for trade in trades], marker='o', linestyle='-', color='b')
plt.title('Trade PnL Over Time')
plt.xlabel('Date')
plt.ylabel('PnL ($)')
plt.grid()
plt.show()
# Save plot to file
plt.savefig('trade_pnl_over_time.png')

print(tabulate(trades, headers="keys", tablefmt="grid"))

# print("\nExits:")
# exit_data = [
#     {
#     'ref': trade.ref,
#     'entry_date': trade.dtopen,
#     'exit_date': trade.dtclose,
#     'exit_price': trade.price,
#     'pnl': trade.pnlcomm,
#     'size': trade.size,
#     }
#     for trade in strat.exit
# ]
# print(tabulate(exit_data, headers="keys", tablefmt="grid"))

total_pnl = sum(round(trade.pnlcomm,2) for trade in strat.exit)

# Print initial portfolio value
print(f"Initial Portfolio Value: {cerebro.broker.startingcash:.2f}")

# Print the new portfolio value
print(f"Final Portfolio Value: {cerebro.broker.getvalue():.2f}")
print(f"Final Cash: {cerebro.broker.getcash():.2f}")

# Print the total PnL
print(f"Total PnL (realized + unrealized): {cerebro.broker.getvalue() - cerebro.broker.startingcash:.2f}")

# Print the trade profit/loss
print(f"Total Realized PnL: {total_pnl:.2f}")

# Print the unrealized PnL
print(f"Unrealized PnL: {cerebro.broker.getvalue() - cerebro.broker.startingcash - total_pnl:.2f}")

# Total Return
print(f"Total Return: {((cerebro.broker.getvalue() - cerebro.broker.startingcash) / cerebro.broker.startingcash) * 100:.2f}%")

# Annualized Return
returns = strat.analyzers.returns.get_analysis()
print(f"Annualized Return: {returns['rnorm100']:.2f}%")

# Average Return
print(f"Average Return: {returns['ravg'] * 100:.2f}%")

# Print the Sharpe Ratio
sharpe = strat.analyzers.sharpe.get_analysis()
print(f"Sharpe Ratio: {sharpe['sharperatio']:.2f}")

# Annualized Sharpe Ratio
sharpe_a = strat.analyzers.sharpe_a.get_analysis()
print(f"Annualized Sharpe Ratio: {sharpe_a['sharperatio']:.2f}")

# Print the maximum drawdown
drawdown = strat.analyzers.drawdown.get_analysis()
print(f"Maximum Drawdown: {drawdown['max']['drawdown']:.2f}%")