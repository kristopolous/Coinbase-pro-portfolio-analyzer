#!/usr/bin/python3
import os
import time
import urllib.request
import json
import secret
import math

one_day = 86400

polo_instance = False
def polo_connect():
    global polo_instance
    if not polo_instance:
        import secret
        from poloniex import Poloniex
        polo_instance = Poloniex(*secret.token)
    return polo_instance

def need_to_get(path, doesExpire = True, expiry = one_day / 2):
    now = time.time()
    if doesExpire:
        return not (os.path.isfile(path) and now < (os.stat(path).st_mtime + expiry))
    else:
        return not os.path.isfile(path)

def btc_price():
    if need_to_get('cache/btc'):
        with open('cache/btc', 'wb') as cache:
            cache.write(urllib.request.urlopen("https://api.coindesk.com/v1/bpi/currentprice.json").read())

    with open('cache/btc') as json_data:
        d = json.load(json_data)
        return d['bpi']['USD']['rate_float']

def trade_history(currency):
    step = one_day * 7
    now = time.time()
    start = math.floor(time.time() / 10000000) * 10000000
    doesExpire = False
    all_trades = []
    for i in range(start, int(now), step):
        if now - start < step:
            doesExpire = true
        name = 'cache/{}-{}.txt'.format(currency, i)
        if need_to_get(name, doesExpire = doesExpire, expiry = 300):
            with open(name, 'w') as cache:
                p = polo_connect() 
                history = p.returnTradeHistory(currencyPair=currency, start=i, end=i + step)
                json.dump(history, cache)

        with open(name) as handle:
            data = handle.read()
            if len(data):
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

    return all_trades
