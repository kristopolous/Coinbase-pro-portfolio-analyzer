#!/usr/bin/python3
import os
import time
import urllib.request
import json


one_day = 86400

def btc_price():
    now = time.time()
    if not os.path.isfile('cache/btc') or now > os.stat('.btc').st_mtime:
        with open('cache/btc', 'wb') as cache:
            cache.write(urllib.request.urlopen("https://api.coindesk.com/v1/bpi/currentprice.json").read())

    with open('cache/btc') as json_data:
        d = json.load(json_data)
        return d['bpi']['USD']['rate_float']

