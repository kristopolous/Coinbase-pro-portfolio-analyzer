#!/usr/bin/python3
import lib
import secret
import time
import sys
from poloniex import Poloniex
p = Poloniex(*secret.token_old)

f = open('/dev/null', 'w')
#sys.stderr = f

margin = 0.0117
unit = 19100
# .005 is accounted for in the trades.
frac = 1 + ((margin - 0.005) * 0.92)
lower = (1 - margin)
upper = 1/lower + 0.00005

while True:
    all_trades = lib.tradeHistory('all', forceUpdate=True)
    cur_balances = {k: v for k, v in lib.returnCompleteBalances().items() if v['btcValue'] > 0.00001}
    positive_balances = {k: v['cur'] for k,v in cur_balances.items() }

    all_prices = lib.returnTicker(forceUpdate = True)
    for k, v in positive_balances.items():
        if k == 'BTC':
            continue

        exchange = "BTC_{}".format(k)
        backwardList = reversed(all_trades[exchange])
        last_trade = all_trades[exchange][-1] 
        last_rate = last_trade['rate']
        sellList = [last_trade['rate']]
        buyList = [last_trade['rate']]
        for trade in backwardList:
            if trade['type'] == 'sell':
                if len(sellList) < 5:
                    sellList.append(trade['rate'])
            else:
                if len(buyList) < 5:
                    buyList.append(trade['rate'])

            if len(buyList) == len(sellList) == 5:
                break

        #print(sellList, buyList)
        last_buy_max = max(buyList)
        last_sell_min = min(sellList)
        #print(last_buy_max, buyList, last_sell_min, sellList)
        #sys.exit(0)
        #last_rate = last_trade['rate']
        current = all_prices[exchange]

        if last_buy_max * upper < current['highestBid']:
            trade_amount = unit * frac
            rate=current['highestBid_orig']
            amount_to_trade = trade_amount / int(rate.lstrip("0."))
            try:
                res = p.sell(currencyPair=exchange, rate=rate, amount=amount_to_trade, orderType="fillOrKill")
                lib.showTrade(res, exchange, trade_type='sell', rate=rate, source='bot2', amount=amount_to_trade)
            except Exception as ex:
                print("  SELL {:9}  {:.3f} {}".format(exchange, 100 * (current['highestBid'] / last_buy_max - 1), ex))


       
        elif last_sell_min * lower > current['lowestAsk']:
            rate=current['lowestAsk_orig']
            amount_to_trade = unit / int(rate.lstrip("0."))
            try:
                res = p.buy(currencyPair=exchange, rate=rate, amount=amount_to_trade, orderType="fillOrKill")
                lib.showTrade(res, exchange, trade_type='buy', rate=rate, source='bot2', amount=amount_to_trade)
            except Exception as ex:
                print("  BUY  {:9} {:.3f} {}".format(exchange, 100 * (current['lowestAsk'] / last_sell_min - 1), ex))
        


    print("------ {} ------".format(time.strftime("%Y-%m-%d %H:%M:%S")))

    time.sleep(15)
