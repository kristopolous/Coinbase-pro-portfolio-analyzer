#!/usr/bin/python3
import time
import sys
import os
import lib
import csv
import json
from datetime import datetime
import fake
from operator import itemgetter, attrgetter
import urllib.request


now = int(time.time()) 

p = lib.connect()
pbal = lib.returnCompleteBalances()
exList = [ 'BTC_{}'.format(k) for k,v in pbal.items() if k != 'BTC' and v['cur'] > 0]

dt = lambda x: datetime.fromtimestamp(x).strftime('(%Y-%m-%d.%H:%M:%S) ')

for ex in exList:
    priceHistoryName = "test/{}-price".format(ex)
    fullHistoryName = "test/{}-full".format(ex)
    start = now - lib.one_day * 120
    uniqueIdList = set()
    historyFull = []
    historyPrice = []
    
    lastEnd = 0
    if not os.path.exists(fullHistoryName):
        while True:
            end = min(now, start + 0.8 * lib.one_day)
            #print("{} {}  {}".format(ex, dt(start), dt(end)))
            snapRaw = urllib.request.urlopen('https://poloniex.com/public?command=returnTradeHistory&currencyPair={}&start={}&end={}'.format(ex, start, end)).read().decode('utf-8')
            snap = json.loads(snapRaw)
            #p.marketTradeHist(ex, start=start, end=end)
            if len(snap) == 0:
                start = min(now, start + (28 * lib.one_day))
                if start == now:
                    break
            else:
                snapOrig = snap
                snapFull = list(filter(lambda x: x['globalTradeID'] not in uniqueIdList, snapOrig))

                for v in snapFull:
                    v['unix'] = int(time.mktime(datetime.strptime(v['date'], '%Y-%m-%d %H:%M:%S').timetuple()))
                    uniqueIdList.add(v['globalTradeID'])

                snapFull = sorted(snapFull, key=itemgetter('unix'))

                #print(*[dt(x) for x in [snapPrice[1][0], snapPrice[-1][0], start, end]])

                if len(snapFull) > 0:
                    historyFull += snapFull
                    oldStart = start
                    frac = 1/3
                    if len(snap) == 50000:
                        frac /= 8
                    start = (snapFull[-1]['unix'] - snapFull[0]['unix']) * (frac) + snapFull[0]['unix'] - (8 * 3600)

                    print("{}  {}    {} {} {}".format(ex, snapFull[0]['date'], snapFull[-1]['date'], len(snapOrig) - len(snapFull), len(snapFull)))
                    lastEnd = snapFull[-1]['unix'] 
                else: 
                    start += 900


        historyPrice = [ (v['unix'], float(v['rate'])) for v in historyFull ]
        with open(priceHistoryName, 'w') as cache:
            handle = csv.writer(cache)
            handle.writerows(sorted(historyPrice, key=itemgetter(0)))

        with open(fullHistoryName, 'w') as cache:
            json.dump(sorted(historyFull, key=itemgetter('unix')), cache)  
