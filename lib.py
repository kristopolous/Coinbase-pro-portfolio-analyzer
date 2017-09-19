#!/usr/bin/python3
import os
import time
import urllib.request
import json
import secret
import math
import re
import sys
from datetime import datetime
from operator import itemgetter, attrgetter

one_day = 86400
first_day = 1501209600

polo_instance = False

def plog(what):
    print(bstr("{} {}".format(time.strftime("%Y-%m-%d %H:%M:%S"), what)))

def bstr(what):
    # there's probably smarter ways to do this ... but
    # I can't think of one
    for i in range(6, 0, -1):
        what = re.sub('^(-?)0\.{}'.format('0' * i), r'\1 .{}'.format('_' * i), what)
        what = re.sub('(\s)(-?)0\.{}'.format('0' * i), r'\1\2 .{}'.format('_' * i), what)

    what = re.sub('^0\.', ' .', what)
    what = re.sub(' (-?)0\.', r' \1 .', what)
    return what 

def bprint(what):
    print(bstr(what))

def polo_connect():
    global polo_instance
    if not polo_instance:
        import secret
        from poloniex import Poloniex
        polo_instance = Poloniex(*secret.token)
    return polo_instance

def need_to_get(path, doesExpire = True, expiry = one_day / 2):
    now = time.time()

    if not os.path.isfile(path) or os.path.getsize(path) < 10:
        return True

    if doesExpire:
        return now > (os.stat(path).st_mtime + expiry)

def cache_get(fn, expiry=300, forceUpdate = False):
    name = "cache/{}".format(fn)
    if need_to_get(name, expiry=expiry) or forceUpdate:
        with open(name, 'w') as cache:
            p = polo_connect() 
            data = getattr(p, fn)()
            json.dump(data, cache)

    with open(name) as handle:
        data = handle.read()
        if len(data) > 10:
            return json.loads(data)

def returnOpenOrders():
    return cache_get('returnOpenOrders', expiry=30)

def returnCompleteBalances():
    balanceMap = toFloat(cache_get('returnCompleteBalances'), ['available', 'onOrders', 'btcValue'])
    for k,v in balanceMap.items():
        balanceMap[k]['cur'] = v['available'] + v['onOrders']

    return balanceMap

def returnTicker(forceUpdate = False):
    return toFloat(cache_get('returnTicker', forceUpdate), ['highestBid', 'lowestAsk', 'last', 'percentChange'])

def btc_price():
    if need_to_get('cache/btc'):
        with open('cache/btc', 'wb') as cache:
            cache.write(urllib.request.urlopen("https://api.coindesk.com/v1/bpi/currentprice.json").read())

    with open('cache/btc') as json_data:
        d = json.load(json_data)
        return d['bpi']['USD']['rate_float']


def analyze(data):
    data = sorted(data, key = lambda x: x['rate'])
    buyList = list(filter(lambda x: x['type'] == 'buy', data))
    sellList = list(filter(lambda x: x['type'] == 'sell', data))

    res = {
        'buyList': buyList,
        'sellList': sellList,
        'lowestBuy': buyList[0]['rate'],
        'highestBuy': buyList[-1]['rate']
    }

    if len(sellList) > 0:
        res['lowestSell'] = sellList[0]['rate']
        res['highestSell'] = sellList[-1]['rate']
        res['avgSell'] = sum([ x['btc'] for x in sellList]) / sum([ x['cur'] for x in sellList]) 

    res['avgBuy'] = sum([ x['btc'] for x in buyList]) / sum([ x['cur'] for x in buyList]) 
    return res


def recent(currency):
    data = tradeHistory(currency)
    buyList = list(filter(lambda x: x['type'] == 'buy', data))
    sellList = list(filter(lambda x: x['type'] == 'sell', data))

    print("Last buy")
    bprint("\n".join([" {} {:.8f} {:.8f}".format(i['date'], i['rate'], i['btc']) for i in reversed(buyList[-5:])]))
    print("Last sell")
    bprint("\n".join([" {} {:.8f} {:.8f}".format(i['date'], i['rate'], i['btc']) for i in reversed(sellList[-5:])]))

def showTrade(order, exchange, trade_type, rate, amount, source='human'):
    currency = exchange[4:]

    for trade in order['resultingTrades']:
        plog("{:9} {}  {}{} at {}BTC. Total {}BTC".format(exchange, trade['type'], trade['amount'], currency, trade['rate'], trade['total']))

    if len(order['resultingTrades']) == 0:
        plog("{:9} Open {} {:.8f} * {:.8f} = {:.8f}btc".format(exchange, trade_type, rate, amount, rate * amount))

    order['type'] = trade_type
    order['rate'] = rate
    order['amount'] = amount

    order['time'] = time.strftime("%Y-%m-%d %H:%M:%S")
    order['exchange'] = exchange
    order['source'] = source

    with open('order-history.json','a') as f:
        f.write("{}\n".format(json.dumps(order)))


def ignorePriorExits(tradeList):
    ttl_btc = 0
    ttl_cur = 0
    recent = []

    for row in tradeList:
        if row['type'] == 'buy':
            ttl_cur += row['cur']
        if row['type'] == 'sell':
            ttl_cur -= row['cur']

        # if we've exited the currency then we reset our
        # counters
        if ttl_cur < 0.0000000001:
            recent = []
            ttl_cur = 0
        else:
            recent.append(row)

    return recent


def toFloat(tradeList, termList):
    if isinstance(tradeList, dict):
        for k, v in tradeList.items():
            for term in termList:
                tradeList[k][term] = float(tradeList[k][term])
    else:
        for i in range(0, len(tradeList)):
            for term in termList:
                tradeList[i][term] = float(tradeList[i][term])

    return tradeList

def historyFloat(tradeList):
    toFloat(tradeList, ['total', 'amount', 'rate', 'fee'])
    for i in range(0, len(tradeList)):

        tradeList[i]['btc'] = tradeList[i]['total']
        tradeList[i]['cur'] = tradeList[i]['amount']

        if tradeList[i]['type'] == 'sell':
            tradeList[i]['btc'] -= tradeList[i]['total'] * tradeList[i]['fee']

        if tradeList[i]['type'] == 'buy':
            tradeList[i]['cur'] -= tradeList[i]['cur'] * tradeList[i]['fee']

        tradeList[i]['date'] = datetime.strptime( tradeList[i]['date'], '%Y-%m-%d %H:%M:%S' )

    return tradeList

def tradeHistory(currency = 'all', forceUpdate = False):
    if currency != 'all':
        all_trades = tradeHistory(forceUpdate = forceUpdate)
        return all_trades[currency]

    step = one_day * 7
    now = time.time()
    start = first_day
    doesExpire = False
    all_trades = []
    for i in range(start, int(now), step):
        if now - i < step:
            doesExpire = True

        name = 'cache/{}-{}.txt'.format(currency, i)
        if need_to_get(name, doesExpire = doesExpire, expiry = 300) or (doesExpire and forceUpdate):
            with open(name, 'w') as cache:
                p = polo_connect() 
                end = i + step
                if end > now:
                    end = False
                history = p.returnTradeHistory(currencyPair=currency, start=i, end=end)
                json.dump(history, cache)

        with open(name) as handle:
            data = handle.read()
            if len(data) > 10:
                json_data = json.loads(data)
                if isinstance(json_data, dict):
                    if not isinstance(all_trades, dict):
                        all_trades = {}

                    for k,v in json_data.items():
                        if k not in all_trades:
                            all_trades[k] = []
                        all_trades[k] += v
                else:
                    all_trades += json_data

    for k,v in all_trades.items():
        all_trades[k] = sorted(historyFloat(v), key=itemgetter('date'))

    return all_trades
