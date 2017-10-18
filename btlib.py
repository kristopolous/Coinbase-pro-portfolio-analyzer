#!/usr/bin/python3
import os
import sqlite3

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

        exists = os.path.exists(sqlname) or os.path.getsize(sqlname) < 10000

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

            conn.commit()

        _handle_cache[cur] = {
          'c': c,
          'conn': conn
        }

    return _handle_cache[cur]

def getHistory(exchange, start, end):
    cur = sqlCursor(cur, createIfNotExists=False)
    if cur:
        where = []
        qstr = 'select * from history'

        if start:
            where.append('date >= {}'.format(start))
        if end:
            where.append('date <= {}'.format(start))

        if len(where):
            qstr += ' where {}'.format(" and ".join(where))

        return all(cur, qstr)



