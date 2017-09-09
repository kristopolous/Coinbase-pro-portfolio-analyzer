#!/usr/bin/python3
import os
import time
import urllib.request
import json

one_day = 86400

def need_to_get(path):
    return os.path.isfile('cache/btc') or now > os.stat('cache/btc').st_mtime + one_day / 2

def btc_price():
    if not os.path.isfile('cache/btc') or now > os.stat('cache/btc').st_mtime:
        with open('cache/btc', 'wb') as cache:
            cache.write(urllib.request.urlopen("https://api.coindesk.com/v1/bpi/currentprice.json").read())

    with open('cache/btc') as json_data:
        d = json.load(json_data)
        return d['bpi']['USD']['rate_float']

