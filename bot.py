#!/usr/bin/python3
import lib
import secret
import time
import sys
from poloniex import Poloniex
p = Poloniex(*secret.token_old)

f = open('/dev/null', 'w')
#sys.stderr = f

margin = 0.0133
min = 10500
# .005 is accounted for in the trades.
frac = 1 + ((margin - 0.005) * 0.92)
#print(frac)

while True:
    all_trades = lib.tradeHistory('all', forceUpdate=True)
    cur_balances = {k: v for k, v in lib.returnCompleteBalances().items() if v['btcValue'] > 0.00001}
    positive_balances = {k: v['cur'] for k,v in cur_balances.items() }

    all_prices = lib.returnTicker(forceUpdate = True)
    for k, v in positive_balances.items():
        if k == 'BTC':
            continue

        exchange = "BTC_{}".format(k)
        last_trade = all_trades[exchange][-1]
        last_rate = last_trade['rate']
        current = all_prices[exchange]

        res = True
        if last_rate * (1 + margin) < current['highestBid']:
            trade_amount = min * frac
            amount_to_trade = trade_amount / int(current['highestBid_orig'].lstrip("0."))
            try:
                res = p.sell(currencyPair=exchange, rate=current['highestBid_orig'], amount=amount_to_trade, orderType="fillOrKill")
                print("       SELL {:9}  {:.3f}".format(exchange, 100 * (current['highestBid'] / last_rate - 1)))
            except Exception as ex:
                print(res, ex)
                print("FAILED SELL {:9}  {:.3f}".format(exchange, 100 * (current['highestBid'] / last_rate - 1)))
                pass

        elif last_rate * (1 - margin) > current['lowestAsk']:
            amount_to_trade = min / int(current['lowestAsk_orig'].lstrip("0."))
            try:
                res = p.buy(currencyPair=exchange, rate=current['lowestAsk_orig'], amount=amount_to_trade, orderType="fillOrKill")
                print("       BUY  {:9} {:.3f}".format(exchange, 100 * (current['lowestAsk'] / last_rate - 1)))
            except Exception as ex:
                print(res, ex)
                print("FAILED BUY  {:9} {:.3f}".format(exchange, 100 * (current['lowestAsk'] / last_rate - 1)))
                pass

    print("------ {} ------".format(time.strftime("%Y-%m-%d %H:%M:%S")))

    time.sleep(15)
