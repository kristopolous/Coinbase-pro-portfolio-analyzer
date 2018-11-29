#!/usr/bin/python3
import lib
import secret
import time
import sys
from poloniex import Poloniex
p = Poloniex(*secret.token_old)

f = open('/dev/null', 'w')
#sys.stderr = f

margin = {
    'buy': 0.0400,
    'sell': 0.0278
}

amount = {
#
# PAY THE FUCK ATTENTION 
# TO THIS AMOUNT IF YOU
# DO NOT WANT TO LOSE 
# MONEY
#
# MAKE SURE THIS SHIT LINES
# UP OTHERWISE YOU MAY BE
# AN ORDER OF MAGNITUDE OFF
# WITH YOUR AMOUNTS
#
#           0.00000000          
    'sell':      12001,
    'buy' :      10500
}
# how far back to look in the history
history = {
    'sell':     4,
    'buy':      6
}

if amount['sell'] > 50000:
    print("Refusing to trade that amount")
    sys.exit(0)

# .005 is accounted for in the trades.
frac = {}
lower = {}
upper = {}

for what in ['buy', 'sell']: 
    frac[what] = 1 + ((margin[what] - 0.005) * 0.92)
    lower[what] = (1 - margin[what])
    upper[what] = 1/lower[what] + 0.00005

cycle = 0

holdList = ['GAS', 'DOGE']#'DGB', 'GNT', 'ZRX', 'RADS', 'DCR']#'XMR', 'ETC']

while True:
    all_trades = lib.tradeHistory('all', forceUpdate=True)
    cur_balances = {k: v for k, v in lib.returnCompleteBalances().items() if v['btcValue'] > 0.00001}
    positive_balances = {k: v['cur'] for k,v in cur_balances.items() }

    all_prices = lib.returnTicker(forceUpdate = True)
    trade_ix = 0
    for k, v in positive_balances.items():
        if k == 'BTC' or k == 'LTC':
            continue

        exchange = "BTC_{}".format(k)
        backwardList = list(reversed(all_trades[exchange]))
        last_trade = all_trades[exchange][-1] 
        maxhistory = max(history['buy'], history['sell'])

        lastList = [x['rate'] for x in all_trades[exchange][-maxhistory:]]
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

        #
        # YOU WANT TO USE THE OPPOSITE ACTION AS THE POINT
        # OF HISTORY TO DETERMINE THE TRADE
        #
        last_buy_max = max(lastList[-history['sell']:])
        last_sell_min = min(lastList[-history['buy']:])

        #last_buy_max = max(buyList)
        #last_sell_min = min(sellList)
        #print(last_buy_max, buyList, last_sell_min, sellList)
        #sys.exit(0)
        #last_rate = last_trade['rate']
        current = all_prices[exchange]

        #
        # -----
        # THIS IS THE SELL BLOCK!!!
        # -----
        #
        if last_buy_max * upper['sell'] < current['highestBid'] and k not in holdList:
            trade_ix += 1
            if trade_ix == 1:
                sys.stdout.write('\n')
            trade_amount = amount['sell'] * frac['sell']
            rate = current['highestBid_orig']
            amount_to_trade = (trade_amount / int(rate.lstrip("0.")))
            try:
                res = p.sell(currencyPair=exchange, rate=rate, amount=amount_to_trade, orderType="fillOrKill")
                lib.showTrade(res, exchange, trade_type='sell', rate=rate, source='bot2', amount=amount_to_trade)
                print("      Spread: {:f}".format( (100 * current['lowestAsk'] / current['highestBid'] ) - 100 ))
            except Exception as ex:
                print("  SELL {:9}  {} {}".format(exchange, rate, ex))


        #
        # -----
        # THIS IS THE BUY BLOCK
        # -----
        # BUY BUY
        #
       
        elif last_sell_min * lower['buy'] > current['lowestAsk'] and k not in holdList:
            trade_ix += 1
            if trade_ix == 1:
                sys.stdout.write('\n')
            rate=current['lowestAsk_orig']
            amount_to_trade = amount['buy'] / int(rate.lstrip("0."))
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

    time.sleep(12)
