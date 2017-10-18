#!/usr/bin/python3
import time
import sys
import os
import lib
import json
import btlib
from datetime import datetime
from dateutil import parser
import sqlite3
from operator import itemgetter, attrgetter
import urllib.request
import calendar

now = int(time.time()) 

exList = lib.returnTicker().keys()

dt = lambda x: datetime.utcfromtimestamp(x).strftime('(%Y-%m-%d.%H:%M:%S) ')
dt2unix = lambda x: int(calendar.timegm(parser.parse(x.replace(' ', 'T')+'Z').timetuple()))

BUY = 0
SELL = 1

def get_recent(cur):
    now = int(time.time()) 
    low, high = btlib.get_bounds(cur)
    if not high:
        high = 0

    earliest = max(high, now - lib.one_day * 120)
    end = now
    lastEnd = 0
    sql = btlib.sqlCursor(cur)

    # the idiots at polo give things in reverse chronological order. what a stupid
    # braindamaged retarded interface. these people are profoundly incompetent retards.
    while True:
        if end < high and end > low:
            end = low

        start = end - 4 * lib.one_day

        print("{}  {} {} {} {} REQUEST".format(ex, dt(start), start, dt(end), end))
        snapRaw = urllib.request.urlopen('https://poloniex.com/public?command=returnTradeHistory&currencyPair={}&start={}&end={}'.format(cur,start, end)).read().decode('utf-8')
        snap = json.loads(snapRaw)

        if len(snap) == 0:
            print("{} No trades found ... bye", dt(start))
            break

        for v in snap:
            v['unix'] = dt2unix(v['date'])

        snap = sorted(snap, key=itemgetter('unix'))

        for v in snap:
            sql['c'].execute("INSERT INTO history VALUES ({}, {}, {}, {}, {}, {})".format(
                v['globalTradeID'], v['unix'], v['total'], v['rate'], v['amount'], BUY if v['type'] == 'buy' else SELL))

        sql['conn'].commit()

        end = snap[0]['unix'] - 1

        print("{}  {} {} {} {} {} {}".format(ex, dt(end), end, dt(snap[-1]['unix']), snap[-1]['unix'], snap[-1]['date'], len(snap)))

        if end < earliest:
            break
        

def data_to_sql(cur):
    sql = btlib.sqlCursor(cur)

    with open(name, 'r') as handle:
        data = handle.read()
        jsonData = json.loads(data)

        ttl = len(jsonData)
        for row in jsonData:
            if ix % 10000 == 0:
                print("{} {:5.2f}% {}".format(cur, ix * 100 / ttl, ix))

            ix += 1
            sql['c'].execute("INSERT INTO history VALUES ({}, {}, {}, {}, {}, {})".format(
                row['globalTradeID'], row['unix'], row['total'], row['rate'], row['amount'], BUY if row['type'] == 'buy' else SELL))



for ex in exList:
    start = now - lib.one_day * 120
    uniqueIdList = set()
    historyFull = []
    historyPrice = []
    
    get_recent(ex)
    continue
    lastEnd = 0

    while True:
        end = min(now, start + 4 * lib.one_day)
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
