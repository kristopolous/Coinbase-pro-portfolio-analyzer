#!/usr/bin/python3
import time
import sys
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

    if not low:
        low = 0

    high += 1
    low -= 1

    low_bound = now - lib.one_day *210
    earliest = max(high, low_bound)
    end = now
    lastEnd = 0
    sql = btlib.sqlCursor(cur)

    # the idiots at polo give things in reverse chronological order. what a stupid
    # braindamaged retarded interface. these people are profoundly incompetent retards.
    while True:
        if end < high and end > low:
            end = low

        start = max(end - 9 * lib.one_day, earliest)
        if start == high:
            print("Skipping over existing data")
            end = low
            earliest = low_bound
            start = max(end - 9 * lib.one_day, earliest)

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
    get_recent(ex)
