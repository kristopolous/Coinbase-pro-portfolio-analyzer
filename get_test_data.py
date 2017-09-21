#!/usr/bin/python3
import time
import sys
import os
import lib
import csv
from datetime import datetime
import fake
from operator import itemgetter, attrgetter


now = int(time.time()) 

p = lib.connect()
pbal = lib.returnCompleteBalances()
exList = [ 'BTC_{}'.format(k) for k,v in pbal.items() if k != 'BTC' and v['cur'] > 0]

dt = lambda x: datetime.fromtimestamp(x).strftime('(%Y-%m-%d.%H:%M:%S) ')

for ex in exList:
    name = "test/{}".format(ex)
    start = now - lib.one_day * 20
    history = []
    if not os.path.exists(name):
        while True:
            end = min(now, start + 0.25 * lib.one_day)
            snap =  p.marketTradeHist(ex, start=start, end=end)
            if len(snap) == 0:
                start = min(now, start + (28 * lib.one_day))
                if start == now:
                    break
            else:

                snap = [ (int(time.mktime(datetime.strptime(v['date'], '%Y-%m-%d %H:%M:%S').timetuple())), float(v['rate'])) for v in snap ]
                snap = sorted(snap, key=itemgetter(0))

                print(*[dt(x) for x in [snap[0][0], snap[-1][0], start, end]])
                history += snap
                start = snap[-1][0] + 1


        with open(name, 'w') as cache:
            handle = csv.writer(cache)
            handle.writerows(sorted(history, key=itemgetter(0)))

