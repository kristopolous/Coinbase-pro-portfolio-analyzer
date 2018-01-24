#!/usr/bin/python3
import os
import sqlite3

# Many talib functions use periods, which are slots of trading broken up into time periods
# this is the period duration in seconds for the slots
PERIOD = 100
_handle_cache = {}

def get_bounds(cur):
    return one(sqlCursor(cur), 'select min(date),max(date) from history')

def all(handle, sql):
    return handle['c'].execute(sql).fetchall()

def one(handle, sql):
    return handle['c'].execute(sql).fetchone()

def sqlCursor(cur, createIfNotExists=True):
    global _handle_cache

    if not cur in _handle_cache:
        sqlname = "test/{}-full.sql".format(cur)

        exists = os.path.exists(sqlname) and os.path.getsize(sqlname) > 10000

        if not createIfNotExists and not exists:
            return Null

        conn = sqlite3.connect(sqlname)
        c = conn.cursor()

        if not exists:
            c.execute('''CREATE TABLE IF NOT EXISTS history (
                    gid integer not null, 
                    date integer not null, 
                    total real not null, 
                    rate real not null, 
                    amount real not null,
                    type integer)''')

            c.execute('CREATE UNIQUE INDEX idx_history_gid ON history (gid)');
            c.execute('create index idx_date on history(date)');

            conn.commit()

        _handle_cache[cur] = {
          'c': c,
          'conn': conn
        }

    return _handle_cache[cur]

def getHistory(exchange, start, end, fieldList='*'):
    cur = sqlCursor(exchange, createIfNotExists=False)
    if cur:
        where = []
        qstr = 'select {} from history'.format(fieldList)

        if start:
            where.append("date >= strftime('%s', '{}')".format(start))
        if end:
            where.append("date <= strftime('%s', '{}')".format(end))

        if len(where):
            qstr += ' where {}'.format(" and ".join(where))

        print(qstr)
        res = all(cur, qstr)
        if len(res) > 0 and len(res[0]) == 1:
            return list(sum(res,()))
        return res


def getPeriods(history, period=PERIOD):
    res = {
        'open': [],
        'high': [],
        'low': [],
        'close': [],
        'period': period
    }

