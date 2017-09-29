#!/usr/bin/python3
import time
import sys
import os
import lib
import json
from datetime import datetime
from dateutil import parser
import sqlite3
from operator import itemgetter, attrgetter
import urllib.request

now = int(time.time()) 

exList  = lib.returnTicker().keys()

dt = lambda x: datetime.fromtimestamp(x).strftime('(%Y-%m-%d.%H:%M:%S) ')
dt2unix = lambda x: int(time.mktime(parser.parse(x.replace(' ', 'T')+'Z').timetuple()))

BUY = 0
SELL = 1

def get_bounds(cur):
    name = "test/{}-full.sql".format(cur)

    if os.path.exists(name):
        conn = sqlite3.connect(name)
        c = conn.cursor()
        res = c.execute('select max(date),min(date) from history')
        return res

    return False


def data_to_sql(cur):
    name = "test/{}-full".format(cur)
    sqlname = "{}.sql".format(name)
    ix = 0

    if os.path.exists(sqlname) and os.path.getsize(sqlname) > 100000:
        return

    with open(name, 'r') as handle:
        data = handle.read()
        jsonData = json.loads(data)
        conn = sqlite3.connect(sqlname)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS history (
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
    fullHistoryName = "test/{}-full".format(ex)
    start = now - lib.one_day * 120
    uniqueIdList = set()
    historyFull = []
    historyPrice = []
    
    lastEnd = 0
    if not os.path.exists(fullHistoryName):
        while True:
            end = min(now, start + lib.one_day)
            #print("{} {}  {}".format(ex, dt(start), dt(end)))
            snapRaw = urllib.request.urlopen('https://poloniex.com/public?command=returnTradeHistory&currencyPair={}&start={}&end={}'.format(ex, start, end)).read().decode('utf-8')
            snap = json.loads(snapRaw)

            if len(snap) == 0:
                start = min(now, start + (28 * lib.one_day))
                if start == now:
                    break
            else:
                snapOrig = snap
                snapFull = list(filter(lambda x: x['globalTradeID'] not in uniqueIdList, snapOrig))

                for v in snapFull:
                    v['unix'] = dt2unix(v['date'])
                    uniqueIdList.add(v['globalTradeID'])

                snapFull = sorted(snapFull, key=itemgetter('unix'))

                #print(*[dt(x) for x in [snapPrice[1][0], snapPrice[-1][0], start, end]])

                if len(snapFull) > 0:
                    deltaSinceLast = (snapFull[0]['unix'] - lastEnd) / 60

                    historyFull += snapFull
                    oldStart = start
                    frac = 1
                    if len(snap) == 50000:
                        frac /= 5

                    if deltaSinceLast > 15 and lastEnd > 0 and len(snapOrig) - len(snapFull) == 0:
                        start -= (60 * 45)
                    else:
                        start = max(start + 1, (snapFull[0]['unix'] - snapFull[0]['unix']) * frac + snapFull[0]['unix'])

                    print("{}  {}    {} {:8d} {:.2f}".format(ex, snapFull[0]['date'], snapFull[-1]['date'], len(snapOrig) - len(snapFull), deltaSinceLast))
                    lastEnd = snapFull[-1]['unix'] 
                else: 
                    start += 900


        with open(fullHistoryName, 'w') as cache:
            json.dump(sorted(historyFull, key=itemgetter('unix')), cache)  

    if os.path.exists(fullHistoryName):
        data_to_sql(ex)
