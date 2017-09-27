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


now = int(time.time()) 

p = lib.connect()
pbal = lib.returnCompleteBalances()
exList = [ 'BTC_{}'.format(k) for k,v in pbal.items() if k != 'BTC' and v['cur'] > 0]

dt = lambda x: datetime.fromtimestamp(x).strftime('(%Y-%m-%d.%H:%M:%S) ')

for ex in exList:
    priceHistoryName = "test/{}-price".format(ex)
    fullHistoryName = "test/{}-full".format(ex)
    start = now - lib.one_day * 120
    historyFull = []
    historyPrice = []

    if not os.path.exists(fullHistoryName):
        while True:
            end = min(now, start + 0.2 * lib.one_day)
            snap = p.marketTradeHist(ex, start=start, end=end)
            if len(snap) == 0:
                start = min(now, start + (28 * lib.one_day))
                if start == now:
                    break
            else:

                snapFull = snap
                snapPrice = [ (int(time.mktime(datetime.strptime(v['date'], '%Y-%m-%d %H:%M:%S').timetuple())), float(v['rate'])) for v in snap ]
                snapPrice = sorted(snapPrice, key=itemgetter(1))

                print("{} {} {:.1f} {:.1f} {}".format(ex, snapFull[0]['date'], (snapPrice[-1][0] - end) / 60, (snapPrice[-1][0] - start) / 60, len(snap)))
                #print(*[dt(x) for x in [snapPrice[0][0], snapPrice[-1][0], start, end]])
                for v in snapFull:
                    v['unix'] = int(time.mktime(datetime.strptime(v['date'], '%Y-%m-%d %H:%M:%S').timetuple()))

                historyPrice += snapPrice
                historyFull += snapFull
                start = snapPrice[-1][0] + 1


        with open(priceHistoryName, 'w') as cache:
            handle = csv.writer(cache)
            handle.writerows(sorted(historyPrice, key=itemgetter(0)))

        with open(fullHistoryName, 'w') as cache:
            json.dump(sorted(historyFull, key=itemgetter('unix')), cache)  
