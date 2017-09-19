#!/usr/bin/python3
import time
import sys
import json
import os
import lib
import fake

if len(sys.argv) > 1:
    currency = 'BTC_{}'.format(sys.argv[1].upper())

pList = lib.returnTicker(forceUpdate = True)
rate = pList[currency]['lowestAsk']

fee = 0.0025
unit = 0.0001001

def should_act(currency, margin=0.05):
    pList = lib.returnTicker(forceUpdate = True)
    data = lib.tradeHistory(currency)
    strike = find_next(data)
    if strike:
        sell_price = strike * (1 + margin)
        buy_price = strike * (1 - margin)
    # if we can't find anything then we can go off our averages
    else:
        analyzed = lib.analyze(data)
        sortlist = sorted(data, key = lambda x: x['rate'])
        sell_price = analyzed['avgBuy'] * (1 + margin)
        if not 'avgSell' in analyzed:
            buy_price = analyzed['avgBuy'] - (1 + margin)
        else:
            buy_price = analyzed['avgSell'] - (1 + margin)
    order = False
    
    buy_rate = pList[currency]['lowestAsk'] - 0.00000001
    sell_rate = pList[currency]['highestBid'] + 0.00000001
    
    if buy_rate < buy_price:

        p = lib.polo_connect() 
        amount_to_trade = unit / buy_rate
        order = p.buy(currency, buy_rate, amount_to_trade)
        rate = buy_rate
        trade_type = 'buy'

    elif sell_rate > sell_price:

        p = lib.polo_connect() 
        amount_to_trade = unit / sell_rate
        order = p.sell(currency, sell_rate, amount_to_trade)
        rate = sell_rate
        trade_type = 'sell'

    else:
        lib.plog("{:9} Nothing (buy {:.8f} (now {:.8f}) sell {:.8f} (now {:.8f}))".format(currency, buy_rate, buy_price, sell_rate, sell_price))
        return False

    if order:
        lib.showTrade(order, currency, source='bot', trade_type=trade_type, rate=rate, amount=amount_to_trade)
        return True


def find_next(data):
    sortlist = sorted(data, key = lambda x: x['rate'])
    buyList = list(filter(lambda x: x['type'] == 'buy', sortlist))
    sellList = list(filter(lambda x: x['type'] == 'sell', sortlist))

    # total amount of the currency sold
    ttl_sell_currency = sum([x['amount'] for x in sellList])
    ttl_sell_btc = sum([x['total'] for x in sellList])

    ttl_buy_currency = 0
    ttl_buy_btc = 0
    for x in buyList:
        if ttl_buy_currency >= ttl_sell_currency:
            return x['rate']
            break
        ttl_buy_currency += x['amount']
        ttl_buy_btc += x['total'] 

if __name__ == "__main__":
    lib.bprint("{} @ {:.8f}".format(currency, rate))
    data = lib.tradeHistory(currency, forceUpdate = True)

    next_price = []
    for i in range(0,10):
        strike = find_next(data)
        if strike:
            next_price.append(find_next(data))
        fake.sell(data, 0.0005 / rate, rate)

    marker = {True: '*', False: ' '}
    for p_int in range(100,120,2):
        p = float(p_int)/ 100
        lib.bprint ("{:.2f} {}".format(p, "\t".join(["{} {:.8f}".format(marker[rate > i * p], i * p) for i in next_price])))

    lib.recent(currency)
