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
unit = 7 * 10000
# .005 is accounted for in the trades.
frac = 1 + ((margin - 0.005) * 0.92)
lower = (1 - margin)
upper = 1/lower + 0.00005
cycle = 0

while True:
    all_trades = lib.tradeHistory('all', forceUpdate=True)
    cur_balances = {k: v for k, v in lib.returnCompleteBalances().items() if v['btcValue'] > 0.00001}
    positive_balances = {k: v['cur'] for k,v in cur_balances.items() }

    all_prices = lib.returnTicker(forceUpdate = True)
    trade_ix = 0
    for k, v in positive_balances.items():
        if k == 'BTC':
            continue

        exchange = "BTC_{}".format(k)
        backwardList = list(reversed(all_trades[exchange]))
        last_trade = all_trades[exchange][-1] 
        histLen = 5
        lastList = [x['rate'] for x in all_trades[exchange][-histLen:]]
        """
        last_rate = last_trade['rate']
        sellList = [last_trade['rate']]
        buyList = [last_trade['rate']]
        for trade in backwardList:
            if trade['type'] == 'sell':
                if len(sellList) < histLen:
                    sellList.append(trade['rate'])
            else:
                if len(buyList) < histLen:
                    buyList.append(trade['rate'])

            if len(buyList) == len(sellList) == histLen:
                break
        """
        #print(sellList, buyList)
        last_buy_max = max(lastList)
        last_sell_min = min(lastList)
        #last_buy_max = max(buyList)
        #last_sell_min = min(sellList)
        #print(last_buy_max, buyList, last_sell_min, sellList)
        #sys.exit(0)
        #last_rate = last_trade['rate']
        current = all_prices[exchange]

        if last_buy_max * upper < current['highestBid']:
            trade_ix += 1
            if trade_ix == 1:
                sys.stdout.write('\n')
            trade_amount = unit * frac
            rate=current['highestBid_orig']
            amount_to_trade = trade_amount / int(rate.lstrip("0."))
            try:
                res = p.sell(currencyPair=exchange, rate=rate, amount=amount_to_trade, orderType="fillOrKill")
                lib.showTrade(res, exchange, trade_type='sell', rate=rate, source='bot2', amount=amount_to_trade)
                print("Spread: {:.8f}".format( current['highestBid'] / current['lowestAsk'] ))
            except Exception as ex:
                print("  SELL {:9}  {} {}".format(exchange, rate, ex))


       
        elif last_sell_min * lower > current['lowestAsk']:
            trade_ix += 1
            if trade_ix == 1:
                sys.stdout.write('\n')
            rate=current['lowestAsk_orig']
            amount_to_trade = unit / int(rate.lstrip("0."))
            try:
                res = p.buy(currencyPair=exchange, rate=rate, amount=amount_to_trade, orderType="fillOrKill")
                lib.showTrade(res, exchange, trade_type='buy', rate=rate, source='bot2', amount=amount_to_trade)
                print("Spread: {:.8f}".format( current['highestBid'] / current['lowestAsk'] ))
            except Exception as ex:
                print("  BUY  {:9} {} {}".format(exchange, rate, ex))
        


    if trade_ix > 0:
        sys.stdout.write(time.strftime("%Y-%m-%d %H:%M:%S"))
        cycle = 19
    else:
        cycle += 1
        sys.stdout.write('.')
        if cycle == 64:
            sys.stdout.write('\n')
            cycle = 0
    sys.stdout.flush()

    time.sleep(4)
