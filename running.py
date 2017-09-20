#!/usr/bin/python3
import time
import sys
import json
import os
import lib
import fake
from colors import *

if len(sys.argv) > 1:
    currency = 'BTC_{}'.format(sys.argv[1].upper())

pList = lib.returnTicker(forceUpdate = True)
rate = pList[currency]['lowestAsk']

fee = 0.0025
unit = 0.00010003

def graph_make(buy_price, market_low, market_high, sell_price, margin_buy, margin_sell):
    tmp_avg = sum([buy_price, sell_price])/2 * (1 - (margin_sell - margin_buy) / 2 )
    tmp_len = 125

    delta = 1.25 * (margin_buy + margin_sell)
    low_bar = (1 - delta) * tmp_avg
    high_bar = (1 + delta) * tmp_avg
    tmp_range = high_bar - low_bar
    graph = [""] * tmp_len

    point = lambda val: int((tmp_len - 1) * min(max(val - low_bar, 0), tmp_range) / tmp_range)

    low_index = point(buy_price)
    high_index = point(sell_price)

    graph[0] = '\x1b[35m'
    graph[high_index] = '\x1b[36m'

    for i in range(0, tmp_len):
        if i < low_index or i > high_index:
            graph[i] += '-' 
        else: 
            graph[i] += ' '  

    low_index = point(market_low)
    high_index = point(market_high)
    graph[low_index] += '\x1b[42m'
    if high_index == low_index:
        high_index = min(1 + low_index, tmp_len - 1)
    graph[high_index] += '\x1b[49m'
    
    graph[tmp_len - 1] += '\x1b[0m'
    return "".join(graph)

def please_skip(exchange, margin_buy, margin_sell, extra = ""):
    return should_act(exchange, margin_buy, margin_sell, please_skip = True, extra = extra)

def should_act(exchange, margin_buy, margin_sell, please_skip = False, extra = ""):
    currency = exchange[4:]
    pList = lib.returnTicker()
    data = lib.tradeHistory(exchange, forceCache=True)
    balanceMap = lib.returnCompleteBalances(forceCache = True)

    strike = find_next(data)
    if strike:
        sell_price = strike * (1 + margin_sell)
        buy_price = strike * (1 - margin_buy)
    # if we can't find anything then we can go off our averages
    else:
        analyzed = lib.analyze(data)
        sortlist = sorted(data, key = lambda x: x['rate'])
        sell_price = analyzed['lowestBuy'] * (1 + margin_sell)
        buy_price = analyzed['lowestBuy'] * (1 - margin_buy)

    order = False
    
    market_low =  pList[exchange]['highestBid']
    market_high = pList[exchange]['lowestAsk'] 
    buy_rate = pList[exchange]['lowestAsk'] - 0.00000001
    sell_rate = pList[exchange]['highestBid'] + 0.00000001
    
    graph = graph_make(buy_price, market_low, market_high, sell_price, margin_buy, margin_sell)
    market_graphic = "{:.8f} ({:.8f}{:.8f} ){:.8f} {}".format(buy_price, market_low, market_high, sell_price, graph)

    if please_skip:
        lib.plog("{:5} {:6} {} {:4}".format(currency, '*SKIP*', market_graphic, extra))
        return False

    if buy_rate < buy_price:

        p = lib.polo_connect() 
        amount_to_trade = unit / buy_rate
        order = p.buy(exchange, buy_rate, amount_to_trade)
        rate = buy_rate
        trade_type = 'buy'

    elif sell_rate > sell_price:

        p = lib.polo_connect() 
        amount_to_trade = unit / sell_rate
        if amount_to_trade < balanceMap[currency]['available']:
            try:
                order = p.sell(exchange, sell_rate, amount_to_trade)
                rate = sell_rate
                trade_type = 'sell'
            except:
                lib.plog("{:9} Failed sell {:.8f} @ {:.8f} (bal: {:.8f})".format(exchange, amount_to_trade, buy_price, balanceMap[currency]['available']))

    else:
        lib.plog("{:5} {:6} {} {:4}".format(currency, "", market_graphic, extra))
        return False

    if order:
        lib.showTrade(order, exchange, source='bot', trade_type=trade_type, rate=rate, amount=amount_to_trade, doPrint=False)
        lib.plog("{:5} {:6} {}".format(currency, trade_type, market_graphic))
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
