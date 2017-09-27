#!/usr/bin/python3
import time
import sys
import os
import lib
import csv
import json
from datetime import datetime
import fake
import sqlite3
from operator import itemgetter, attrgetter
import urllib.request


now = int(time.time()) 

p = lib.connect()
pbal = lib.returnCompleteBalances()
exList = [ 'BTC_{}'.format(k) for k,v in pbal.items() if k != 'BTC' and v['cur'] > 0]

dt = lambda x: datetime.fromtimestamp(x).strftime('(%Y-%m-%d.%H:%M:%S) ')

BUY = 0
SELL = 1
def data_to_sql(cur):
    name = "test/{}-full".format(cur)
    ix = 0
    with open(name, 'r') as handle:
        data = handle.read()
        jsonData = json.loads(data)
        conn = sqlite3.connect("{}.sql".format(name))
        """
        "tradeID": 985843, "date": "2017-05-30 08:48:41", "total": "0.09633736", "type": "buy", "rate": "0.00009308", "globalTradeID": 148066353, "unix": 1496159321, "amount": "1034.99532304"
        """
        c = conn.cursor()
        c.execute('''CREATE TABLE history (
                gid integer not null, 
                date integer not null, 
                total real not null, 
                rate real not null, 
                amount real not null,
                type integer)''')
        c.execute('CREATE UNIQUE INDEX idx_history_gid ON history (gid)');

        ttl = len(jsonData)
        for row in jsonData:
            if ix % 10000 == 0:
                print("{} {:5.2f}% {}".format(cur, ix * 100 / ttl, ix))

            ix += 1
            c.execute("INSERT INTO history VALUES ({}, {}, {}, {}, {}, {})".format(
                row['globalTradeID'], row['unix'], row['total'], row['rate'], row['amount'], BUY if row['type'] == 'buy' else SELL))

        conn.commit()
        conn.close()


for ex in exList:
    priceHistoryName = "test/{}-price".format(ex)
    fullHistoryName = "test/{}-full".format(ex)
    start = now - lib.one_day * 120
    uniqueIdList = set()
    historyFull = []
    historyPrice = []
    
    lastEnd = 0
    if os.path.exists(fullHistoryName):
        data_to_sql(ex)
    else:
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
                        frac /= 20
                    start = max(start + 1, (snapFull[-1]['unix'] - snapFull[0]['unix']) * (frac) + snapFull[0]['unix'] - (9 * 3600))

                    print("{}  {}    {} {:8d} {:.2f}".format(ex, snapFull[0]['date'], snapFull[-1]['date'], len(snapOrig) - len(snapFull), (snapFull[0]['unix'] - lastEnd) / 60))
                    lastEnd = snapFull[-1]['unix'] 
                else: 
                    start += 900


        historyPrice = [ (v['unix'], float(v['rate'])) for v in historyFull ]
        with open(priceHistoryName, 'w') as cache:
            handle = csv.writer(cache)
            handle.writerows(sorted(historyPrice, key=itemgetter(0)))

        with open(fullHistoryName, 'w') as cache:
            json.dump(sorted(historyFull, key=itemgetter('unix')), cache)  
