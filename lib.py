#!/usr/bin/python3
import os
import time
import urllib.request
import json
import secret
import math
import re
import sys
import calendar
#import fake
from decimal import *
from dateutil import parser
from datetime import datetime
from operator import itemgetter, attrgetter

one_day = 86400
first_day = 1501209600
is_fake = False
polo_instance = False
MIN = 0.00010002
satoshi_sig = 8
satoshi = 1e-8

_cache = {}

getcontext().prec = 2 * satoshi_sig

str2date = lambda x: parser.parse(x.replace(' ', 'T')+'Z')
str2unix = lambda x: int(calendar.timegm(str2date(x).timetuple()))
str2local = lambda x: int(time.mktime(str2date(x).timetuple()))

def getCurrency():
    currency_list = []
    for i in sys.argv[1:]:
        currency_list.append('BTC_{}'.format(i.upper()))

    if len(currency_list) == 1:
        return currency_list[0]
    if len(currency_list) == 0:
        return False
    return currency_list

def wait(sec):
    if is_fake:
        connect().time += sec
        time.sleep(0.0001)
    else:
        time.sleep(sec)

def plog(what):
    print(bstr("{}".format(what)))
    #print(bstr("{} {}".format(time.strftime("%Y-%m-%d %H:%M:%S"), what)))

def bstr(what):
    # there's probably smarter ways to do this ... but
    # I can't think of one
    for i in range(8, 0, -1):
        what = re.sub('^(-?)0\.{}'.format('0' * i), r'\1 .{}'.format('_' * i), what)
        what = re.sub('([^0-9])0\.{}'.format('0' * i), r'\1 .{}'.format('_' * i), what)

    what = re.sub('^0\.', ' .', what)
    what = re.sub('([^0-9])0\.', r'\1 .', what)
    return what 

def bprint(what):
    print(bstr(what))

def connect():
    if is_fake:
        return fake.connect()

    global polo_instance
    if not polo_instance:
        import secret
        from poloniex import Poloniex
        polo_instance = Poloniex(*secret.token)
    return polo_instance

def need_to_get(path, doesExpire = True, failOnSmall = True, expiry = one_day / 2):
    now = time.time()

    if not os.path.isfile(path) or (failOnSmall and os.path.getsize(path) < 10):
        return True

    if doesExpire:
        return now > (os.stat(path).st_mtime + expiry)

def cache_get(fn, expiry=300, forceUpdate = False, forceCache = False):
    name = "cache/{}".format(fn)
    if not forceCache and ( need_to_get(name, expiry=expiry) or forceUpdate ):
        p = connect() 
        data = getattr(p, fn)()

        if is_fake:
            return data

        with open(name, 'w') as cache:
            json.dump(data, cache)

    with open(name) as handle:
        data = handle.read()
        if len(data) > 10:
            return json.loads(data)

def returnOpenOrders(expiry=30):
    return cache_get('returnOpenOrders', expiry=expiry)

def returnCompleteBalances(forceCache = False):
    if forceCache and 'balances' in _cache:
        return _cache['balances']

    balanceMap = toFloat(cache_get('returnCompleteBalances'), ['available', 'onOrders', 'btcValue'])
    for k,v in balanceMap.items():
        balanceMap[k]['cur'] = v['available'] + v['onOrders']

    _cache['balances'] = balanceMap
    return balanceMap

def returnTicker(forceUpdate = False, forceCache = False):
    if forceCache and 'ticker' in _cache:
        return _cache['ticker']

    tickerMap = toFloat(cache_get('returnTicker', forceUpdate = forceUpdate), ['highestBid', 'lowestAsk', 'last', 'percentChange'])
    _cache['ticker'] = tickerMap
    return tickerMap

def btc_price(force = False):
    if need_to_get('cache/btc') or force:
        with open('cache/btc', 'wb') as cache:
            req = urllib.request.Request("https://api.coindesk.com/v1/bpi/currentprice.json", headers={
              'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
            })
            cache.write(urllib.request.urlopen(req).read())

    with open('cache/btc') as json_data:
        d = json.load(json_data)
        return d['bpi']['USD']['rate_float']


def analyze(data, currency, brief = False, sort = 'rate', do_round = True):
    data = sorted(data, key = lambda x: x[sort])
    buyList = list(filter(lambda x: x['type'] == 'buy', data))
    sellList = list(filter(lambda x: x['type'] == 'sell', data))
    ticker = returnTicker()

    buyListRate = sorted(buyList, key = itemgetter('rate'))
    sellListRate = sorted(sellList, key = itemgetter('rate'))

    res = {
        'lowestBuy': 0,
        'highestBuy': 0,
    	'lowestSell': 0,
    	'highestSell': 0,
    	'sellBtc': 0,
    	'sellCur': 0,
    	'buyAvg': 0,
    	'sellAvg': 0,
    	'avg': 0,
        'break': 0,
        'pl': 0
    }

    if len(buyList) > 0:
        res['lowestBuy'] = buyListRate[0]['rate']
        res['highestBuy'] = buyListRate[-1]['rate']

    if not brief:
        res['buyList'] = buyList
        res['sellList'] = sellList

    if len(sellList) > 0:
        res['lowestSell'] = sellListRate[0]['rate']
        res['highestSell'] = sellListRate[-1]['rate']
        res['sellBtc'] = sum([ x['btc'] for x in sellList])
        res['sellCur'] = sum([ x['cur'] for x in sellList]) 
        res['sellAvg'] = res['sellBtc'] / res['sellCur']

    res['buyCur'] = sum([ x['cur'] for x in buyList])
    res['buyBtc'] = sum([ x['btc'] for x in buyList])
    if res['buyCur'] > 0:
        res['buyAvg'] = res['buyBtc'] / res['buyCur']

    res['cur'] = res['buyCur'] - res['sellCur']
    res['btcMargin'] = res['buyBtc'] - res['sellBtc']

    if currency.find('_') == -1:
        market = 'BTC_{}'.format(currency)
    else:
        market = currency

    if market in ticker:
        res['btc'] = res['cur'] * ticker[market]['last']
    else:
        res['btc'] = res['btcMargin']

    if res['cur'] < 1e-11 and res['cur'] > 0:
        res['cur'] = 0
        res['btc'] = 0

    # The breakpoint is what price you need to sell the
    # remaining share in order to get the same btc back
    # out that you put in.
    res['pl'] = res['sellBtc'] - res['buyBtc']

    if res['cur'] > 0:
        res['break'] = -res['pl'] / res['cur']
        res['avg'] = res['btc'] / res['cur'] 

    # after all the calculations are done now we round off the figures to satoshis
    if do_round:
        for x in ['btc', 'cur']: 
            res[x] = round(res[x], satoshi_sig)

    return res

def unixtime():
    if is_fake:
        return connect().time
    return time.time()

def now():
    if is_fake:
        return datetime.fromtimestamp(connect().time).timetuple()
    return time.localtime()

def recent(currency, anal=False):
    if anal:
        buyList = anal['buyList']
        sellList = anal['sellList']
    else:
        data = tradeHistory(currency)
        buyList = list(filter(lambda x: x['type'] == 'buy', data))
        sellList = list(filter(lambda x: x['type'] == 'sell', data))

    #buy_recent = [" {} {:.8f} {:.8f}".format(i['date'], i['btc'], i['rate']) for i in reversed(buyList[-5:])]
    #sell_recent = [" {:12.8f} {:.8f} {:.8f} {}".format(i['cur'], i['rate'], i['btc'], i['date']) for i in reversed(sellList[-8:]) if i['btc'] > 0.00009]
    buy_recent = ["{} {:.8f}".format(i['date'], i['rate']) for i in reversed(buyList[-8:])]
    sell_recent = [" {:.8f} {}".format(i['rate'], i['date']) for i in reversed(sellList[-11:]) if i['btc'] > 0.00009]
    col_wid = len(buy_recent[0])
    print(("{:>" + str(col_wid) + "}   {}").format("Last Buy", "Last Sell"))
    for i in range(0, 8):
        row = ''
        if i < len(buy_recent):
            row += buy_recent[i]
        else:
            row += " " * col_wid
        row += " "
        if i < len(sell_recent):
            row += sell_recent[i]

        bprint(row)


def showTrade(order, exchange, trade_type, rate, amount, source='human', doPrint=True):
    currency = exchange[4:]

    if doPrint:
        for trade in order['resultingTrades']:
            plog("{:10} {:9} {:4} {:>12} * {} = {}".format(trade['tradeID'], exchange, trade['type'], trade['amount'], trade['rate'], trade['total']))

        if len(order['resultingTrades']) == 0:
            amount = float(amount)
            rate = float(rate)
            plog("{} {:9} Open {:4} {:.8f} * {:.8f} ={:.8f}btc".format(order['orderNumber'], exchange, trade_type, rate, amount, rate * amount))

    order['type'] = trade_type
    order['rate'] = rate
    order['amount'] = amount

    order['time'] = time.strftime("%Y-%m-%d %H:%M:%S")
    order['exchange'] = exchange
    order['source'] = source

    if not is_fake:
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
        if ttl_cur < satoshi * 10:
            recent = []
            ttl_cur = 0
        else:
            recent.append(row)

    return recent


def toFloat(tradeList, termList):
    if isinstance(tradeList, dict):
        for k, v in tradeList.items():
            for term in termList:
                tradeList[k][term + "_orig"] = tradeList[k][term]
                tradeList[k][term] = float(tradeList[k][term])
    else:
        for i in range(0, len(tradeList)):
            for term in termList:
                tradeList[i][term + "_orig"] = tradeList[i][term]
                tradeList[i][term] = float(tradeList[i][term])

    return tradeList

def historyFloat(tradeList):
    toFloat(tradeList, ['total', 'amount', 'rate', 'fee'])
    for i in range(0, len(tradeList)):

        tradeList[i]['btc'] = tradeList[i]['total']
        tradeList[i]['cur'] = tradeList[i]['amount']

        if tradeList[i]['type'] == 'buy':
            tradeList[i]['cur'] -= tradeList[i]['cur'] * tradeList[i]['fee']

        if tradeList[i]['type'] == 'sell':
            tradeList[i]['btc'] -= tradeList[i]['total'] * tradeList[i]['fee']

        tradeList[i]['date'] = datetime.fromtimestamp(tradeList[i]['unix'])

    return tradeList

def tradeHistory(currency = 'all', forceUpdate = False, forceCache = False):
    if is_fake:
        forceCache = True

    if currency != 'all':
        all_trades = tradeHistory(forceUpdate = forceUpdate, forceCache = forceCache)
        if currency in all_trades:
            return all_trades[currency]
        else:
            return []

    if forceCache and 'all_trades' in _cache:
        return _cache['all_trades']

    ts_mult = 4
    step = one_day * ts_mult
    now = time.time()
    doesExpire = False
    all_trades = []
    end = (int(now / step) + 1) * step
    lastend = end
    # currently the cache will vomit at 500 trades.
    while end > first_day:
        name = 'cache/{}-{}.txt'.format(currency, end)
        doesExpire = now - end < step

        ttl = 0
        dmax = 0
        dmin = sys.maxsize
        start = end - step

        if (need_to_get(name, doesExpire = doesExpire, expiry = 300, failOnSmall = False) or (doesExpire and forceUpdate)) and not forceCache:
            with open(name, 'w') as cache:
                p = connect() 

                reqend = end
                if end > now:
                    reqend = False

                history = p.returnTradeHistory(start=start, end=reqend)
                if type(history) == dict:
                    for k,v in history.items():
                        for trade in v:
                            ttl += 1
                            trade['unix'] = str2unix(trade['date'])
                            dmax = max(trade['unix'], dmax)
                            dmin = min(trade['unix'], dmin)

                json.dump(history, cache)


        with open(name) as handle:
            ttl = 0
            dmax = 0
            dmin = sys.maxsize
            data = handle.read()
            if len(data) > 2:
                json_data = json.loads(data)
                if isinstance(json_data, dict):
                    if not isinstance(all_trades, dict):
                        all_trades = {}

                    for k,v in json_data.items():
                        if k not in all_trades:
                            all_trades[k] = []
                        ttl += len(v)
                        dmax = max(max([trade['unix'] for trade in v ]), dmax)
                        dmin = min(min([trade['unix'] for trade in v ]), dmin)
                        all_trades[k] += v
                else:
                    all_trades += json_data

        #if ttl > 0:
        #    print("{:5d}".format(ttl), start, end, "{:4d}".format(int((lastend - end) / 60 / 60)), dmin, dmax, dmax-dmin, start < dmin <= dmax < end)
        #    lastend = end
        if ttl == 500:
            end = dmin - 1
        else:
            end -= step


    for k,v in all_trades.items():
        all_trades[k] = sorted(historyFloat(v), key=itemgetter('date'))

    _cache['all_trades'] = all_trades
    return all_trades
