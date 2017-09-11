#!/usr/bin/python3
import os
import time
import urllib.request
import json

one_day = 86400

polo_instance = False
def polo_connect():
    global polo_instance
    if not polo_instance:
        import secret
        from poloniex import Poloniex
        polo_instance = Poloniex(*secret.token)
    return polo_instance

def need_to_get(path):
    now = time.time()
    return not (os.path.isfile(path) and now < (os.stat(path).st_mtime + one_day / 2))

def btc_price():
    if need_to_get('cache/btc'):
        with open('cache/btc', 'wb') as cache:
            cache.write(urllib.request.urlopen("https://api.coindesk.com/v1/bpi/currentprice.json").read())

    with open('cache/btc') as json_data:
        d = json.load(json_data)
        return d['bpi']['USD']['rate_float']

