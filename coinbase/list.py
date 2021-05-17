#!/usr/bin/python3
import secret
import os
import cbpro 
import hashlib
import json
import sys
import logging
import argparse
import types
import re
import redis
import time

from operator import itemgetter
from dateutil import parser
from decimal import *
getcontext().prec = 2

history = {}
historySet = set()
balanceMap = {}

# a base64 uuidv4 to act as the redis prefix
RPREFIX = 'JfB6wciaRLOrVqbMasWdXQ'
START = time.time()
LAST = START

def clock(what):
    global LAST
    now = time.time()
    print("TTL: {:4.5f} | DELTA: {:4.5f} | {}".format(now - START, now - LAST, what))
    LAST = now
    
def gol(amount):
    sign = '+' if amount >= 0 else ''
    return "{}{:<4d}".format(sign, round(amount))

def hash(*kw):
    return hashlib.md5(json.dumps(kw).encode('utf-8')).hexdigest()

class bypass:
    def __init__(self, secret):
        self.last = None
        self.real = None
        self.secret = secret
        self.ordercache = r.hgetall('coinhash')

    def connect(self):
        if not self.real: 
            self.real = cbpro.AuthenticatedClient(self.secret.key, self.secret.b64secret, self.secret.passphrase)
        return self.real

    def clearcache(self, method, args):
       name = "cache/{}".format(hash(method, args))
       if os.path.isfile(name):
           logging.info("Removing {} for {} {}".format(name, method, args))
           os.remove(name)
       else:
           logging.warning("No file: {}".format(name))

    def invalidate_last(self):
        if os.path.exists(self.last):
            logging.debug("Removing {}".format(self.last))
            os.unlink(self.last)

    def __getattr__(self, method):
        def cb(*args):
            global cli_args
            # We are going to skip over the caching system
            # until we figure out a bit more about how the 
            # system has changed
            key = hash(method, args)

            if method in ['get_product_ticker', 'get_accounts']:
                data = r.get("{}:cb:{}".format(RPREFIX,key))
                if not data:
                    self.connect()
                    data = getattr(self.real, method)(*args)

                    r.set("{}:cb:{}".format(RPREFIX, key), json.dumps(data), 60 * 60)
                else:
                    data = json.loads(data)
                return data

            # getorder for a specific order id *should* always
            # return the same thing.
            elif method == 'get_order':
                # we first try to get the value from the cache
                try:
                    data = self.ordercache.get(key)
                    if data:
                        return json.loads(data)
                    else:
                        self.connect()
                        data = getattr(self.real, method)(*args)

                        if isinstance(data, types.GeneratorType):
                            data_list = [x for x in data]
                            data = data_list

                        r.hset('coinhash', key, json.dumps(data))
                    return data


                except Exception as ex:
                    self.connect()
                    return getattr(self.real, method)(*args)

            else:
                name = "cache/{}".format(key)
                self.last = name

                if cli_args.update :
                    self.clearcache(method, args)

                if not os.path.isfile(name):
                    logging.debug("need to cache ({}, {}) -> {}".format(method, args, name))
                    self.connect()
                    data = getattr(self.real, method)(*args)

                    if isinstance(data, types.GeneratorType):
                        data_list = [x for x in data]
                        data = data_list

                    try:
                        with open(name, 'w') as cache:
                            json.dump(data, cache)
                    except:
                        logging.warning("Unable to cache: ({} {}), {} -> {}".format(method, *args, data, name))

                try:
                    with open(name) as handle:
                        return json.loads(handle.read())

                except Exception as ex:
                    self.invalidate_last()
                    self.connect()
                    return getattr(self.real, method)(*args)

        return cb
            
            
def add(exchange, kind, rate, amount, size, date, obj):
    global history
    global historySet
    global cli_args

    if exchange not in history:
        history[exchange] = {'buycur':0, 'buyusd':0, 'sellcur':0, 'sellusd':0, 'all': []}
        history[exchange]['recent'] = list(map(lambda x: {
            'ttl': x, 
            'sellcount': x, 
            'buycount': x, 
            'buycur': 0, 
            'buyusd': 0, 
            'sellcur': 0, 
            'sellusd': 0
        }, range(cli_args.start, cli_args.end, cli_args.step)))

    if obj['id'] not in historySet:
        historySet.add(obj['id'])
        amount = float(amount)

        cur = '{}cur'.format(kind)
        usd = '{}usd'.format(kind)
        checker = '{}count'.format(kind)

        history[exchange][cur] += amount / float(rate)
        history[exchange][usd] += amount

        for row in history[exchange]['recent']:
            if row[checker] > 0:
                row[cur] += amount / float(rate)
                row[usd] += amount
                row[checker] -= amount

        history[exchange]['all'].append([kind, round(float(rate)), amount, size, parser.parse(date)])

def crawl():
    import datetime
    global cli_args
    global balanceMap

    ix = 0
    for account in account_list:

        balanceMap[account['currency']] = float(account['balance'])
        history = auth_client.get_account_history(account['id'])

        for order in history:
            if not isinstance(order, dict):
                continue

            if cli_args.goback: 
                ix += 1
                if ix > cli_args.goback:
                    continue

            if cli_args.query and order.get('details') and 'product_id' in order['details']:
                if not re.search(cli_args.query, order['details']['product_id'], re.IGNORECASE):
                    continue

            try:
                details = auth_client.get_order(order['details']['order_id'])
                # print(details)
            except:
                # print(order)
                continue

            if 'side' not in details:
                print(details)
                auth_client.invalidate_last()
                continue

            if cli_args.days:
                if (datetime.datetime.now() - parser.parse(details['done_at']).replace(tzinfo=None)).days > cli_args.days:
                    # this means break and go to the next exchange
                    break


            if details['side'] == 'buy':
                amount = float(details['executed_value']) + float(details['fill_fees'])
            else:
                amount = float(details['executed_value']) + float(details['fill_fees'])

            if 'price' in details:
                rate = details['price']
            else:
                rate = amount / float(details['filled_size'])

            size = float(details['filled_size'])

            add(exchange = details['product_id'], 
                kind = details['side'], 
                amount = amount, 
                date = details['done_at'], 
                size = size, 
                rate = rate, 
                obj = details)

cli_parser = argparse.ArgumentParser(description='Historicals for coinbase pro.')
cli_parser.add_argument("-q", "--query", help="only show exchanges that match a regex")
cli_parser.add_argument("--list", help="list exchanges you're active in", action='store_true')
cli_parser.add_argument("--update", help="update the cache", action='store_true')
cli_parser.add_argument("--debug", help="verbose", action='store_true')
cli_parser.add_argument("--start", help="start value", default=100)
cli_parser.add_argument("--step", help="start value", default=250)
cli_parser.add_argument("--end", help="end value for analysis", default=4000)
cli_parser.add_argument("--goback", help="How many orders to go back", default=0)
cli_parser.add_argument("--days", help="How many days to go back", default=0)
cli_parser.add_argument("--average", help="Just show the averages", action='store_true')
cli_args = cli_parser.parse_args()

for i in ['start','step','end','goback', 'days']:
    setattr(cli_args, i, int(getattr(cli_args, i)))

if cli_args.debug:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.WARNING)

# we "expire" all the redis-cache expire items (prefixed with cb:)
if cli_args.update:
    for key in r.keys('{}:cb:*'.format(RPREFIX)):
        r.delete(key)

r = redis.Redis('localhost', decode_responses=True)
auth_client = bypass(secret)
account_list = auth_client.get_accounts()

if type(account_list) is not list and account_list.get('message'):
    print(account_list)
    print("Maybe ntp update?")
    sys.exit(-1)

logging.debug("Account list {}".format(account_list))

clock("setup")
crawl()
clock("crawl")

for exchange in sorted(history.keys()):
    cur = history[exchange]

    unit = exchange.split('-')[0]
    
    if cli_args.query:
        if not re.search(cli_args.query, exchange, re.IGNORECASE):
            continue

    if cli_args.list:
        print(exchange)
        continue

    if cur['buycur'] == 0:
        continue

    ticker = auth_client.get_product_ticker(exchange)
    if not ticker.get('price'):
        print(ticker)
        continue

    price = float(ticker.get('price'))

    avg_buy = cur['buyusd'] / cur['buycur']
    print(" {:9} buy:  {:8.2f} {:8.2f} {:9.4f} {:6} {:>8.3f} ({:.2f})".format(
            exchange,
            avg_buy,
            cur['buyusd'], 
            cur['buycur'],
            gol((100 * price / avg_buy) - 100),
            balanceMap[unit], 
            balanceMap[unit] * price, 
        ))

    if cur['sellcur'] == 0:
        avg_sell = 0
    else:
        avg_sell = cur['sellusd'] / cur['sellcur']

    if avg_sell:
        delta = gol((100 * price / avg_sell) - 100)
    else:
        delta = '...'

    print("{:8.2f}   sell: {:8.2f} {:8.2f} {:9.4f} {:6} {:>8.3f} ({:.2f})".format(
            price,
            avg_sell,
            cur['sellusd'], 
            cur['sellcur'],
            delta,
            cur['buycur'] - cur['sellcur'],
            (cur['buycur'] - cur['sellcur']) * price
        ))

    if cli_args.average:
        print("")

    else:
        print("RECENT")
        for row in cur['recent']:
            buy = 0
            sell = 0

            if row['buycur'] > 0:
                buy = row['buyusd'] / row['buycur']
            if row['sellcur'] > 0:
                sell = row['sellusd'] / row['sellcur']

            print("\t{:4} buy:  {:.2f} {:.2f} {:.4f} \n\t     sell: {:.2f} {:.2f}\n".format(
                row['ttl'], 
                buy, 
                row['buyusd'], 
                100 * ((sell / buy) - 1), 
                sell, 
                row['sellusd'])
            )

        orderList = reversed(sorted(cur['all'], key=itemgetter(4)))
        orderList = list(orderList)

        if len(list(orderList)) > 0:
            curdate = orderList[0][4].strftime("%Y-%m-%d")
            accum = { 
                'buy': {'usd': 0, 'cur': 0}, 
                'sell': {'usd': 0, 'cur': 0}
            }

            print("ALL")
            # unit price | how much spend | how much of unit
            print("\tside   price  usd   amount date")
            for order in orderList:
                logging.debug(order)
                checkdate = order[4].strftime("%Y-%m-%d")
                kind = order[0]

                if checkdate != curdate:
                    for which in ['buy', 'sell']:
                        rate = 0
                        if accum[which]['cur']:
                            rate = accum[which]['usd'] / accum[which]['cur']

                        print("\t\t{:4} {:8.0f} {:8.2f} {:8.4f} {}".format(
                            which, 
                            rate, 
                            accum[which]['usd'], 
                            accum[which]['cur'], 
                            order[4].strftime("%Y-%m-%d"))
                        )

                    accum = { 'buy': {'usd': 0, 'cur': 0}, 'sell': {'usd': 0, 'cur': 0}}
                    print("\t\t-----")
                    curdate = checkdate
                accum[kind]['usd'] += order[2]
                accum[kind]['cur'] += order[3]

                print("\t{:4} {:5} {:7.2f} {:7.4f} {}".format(
                    kind, 
                    order[1], 
                    order[2], 
                    order[3], 
                    order[4].strftime("%Y-%m-%d %H:%M:%S"))
                )


clock("done")
