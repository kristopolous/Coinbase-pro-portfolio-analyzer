#!/usr/bin/python3
import secret
import os
import cbpro 
import hashlib
import json
import sys
import pdb
import logging
import argparse
import types
import re

from operator import itemgetter
from dateutil import parser
from decimal import *
getcontext().prec = 2

def hash(*kw):
    return hashlib.md5(json.dumps(kw).encode('utf-8')).hexdigest()

class bypass:
    def __init__(self, real):
        self.last = None
        self.real = real

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
            name = "cache/{}".format(hash(method, args))
            self.last = name

            if cli_args.update:
                self.clearcache(method, args)

            if not os.path.isfile(name):
                logging.debug("need to cache ({}, {}) -> {}".format(method, args, name))
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
                return getattr(self.real, method)(*args)

        return cb
            
            
def add(exchange, kind, rate, amount, size, date, obj):
    global history
    global historySet
    global cli_args

    if exchange not in history:
        history[exchange] = {'buycur':0, 'buyusd':0, 'sellcur':0, 'sellusd':0, 'all': []}
        history[exchange]['recent'] = list(map(lambda x: {'ttl': x, 'sellcount': x, 'buycount': x, 'buycur':0, 'buyusd':0, 'sellcur':0, 'sellusd':0}, range(cli_args.start, cli_args.end, cli_args.step)))

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
    for account in account_list:

        history = auth_client.get_account_history(account['id'])
        for order in history:
            if cli_args.query and 'product_id' in order:
                if not re.match(cli_args.query, order['product_id'], re.IGNORECASE):
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
cli_parser.add_argument("--query", help="only show exchanges that match a regex")
cli_parser.add_argument("--list", help="list exchanges you're active in", action='store_true')
cli_parser.add_argument("--update", help="update the cache", action='store_true')
cli_parser.add_argument("--debug", help="verbose", action='store_true')
cli_parser.add_argument("--start", help="start value", default=100)
cli_parser.add_argument("--step", help="start value", default=250)
cli_parser.add_argument("--end", help="start value", default=4000)
cli_args = cli_parser.parse_args()

for i in ['start','step','end']:
    setattr(cli_args, i, int(getattr(cli_args, i)))

if cli_args.debug:
    logging.basicConfig(level=logging.DEBUG)

else:
    logging.basicConfig(level=logging.WARNING)

auth_client = bypass(cbpro.AuthenticatedClient(secret.key, secret.b64secret, secret.passphrase))
account_list = auth_client.get_accounts()

history = {}
historySet = set()
crawl()

for exchange, cur in history.items():
    if cli_args.query:
        if not re.match(cli_args.query, exchange, re.IGNORECASE):
            continue

    print(exchange)
    if cli_args.list:
        continue

    try:
        print("\tbuy:  {:.2f} {:7.2f} {:.4f}\n\tsell: {:.2f} {:7.2f} {:.4f}".format(
            cur['buyusd'] / cur['buycur'], cur['buyusd'], cur['buycur'], cur['sellusd'] / cur['sellcur'], cur['sellusd'], cur['sellcur']))

        for row in cur['recent']:
            buy = 0
            sell = 0

            if row['buycur'] > 0:
                buy = row['buyusd'] / row['buycur']
            if row['sellcur'] > 0:
                sell = row['sellusd'] / row['sellcur']
            print("\t{:4} buy:  {:.2f} {:.2f} {:.4f} \n\t     sell: {:.2f} {:.2f}\n".format(row['ttl'], buy, row['buyusd'], 100 * ((sell / buy) - 1), sell, row['sellusd']))
    except:
        pass
    orderList = reversed(sorted(cur['all'], key=itemgetter(4)))
    """
    for order in orderList:
        print("{:4} {} {:6.2f} {:6.4f} {}".format(order[0], order[1], order[2], 100 * order[3], order[4].strftime("%Y-%m-%d %H:%M:%S")))
    """
    orderList = list(orderList)
    if len(list(orderList)) > 0:
        curdate = orderList[0][4].strftime("%Y-%m-%d")
        accum = { 'buy': {'usd': 0, 'cur': 0}, 'sell': {'usd': 0, 'cur': 0}}

        for order in orderList:
            logging.debug(order)
            checkdate = order[4].strftime("%Y-%m-%d")
            kind = order[0]
            if checkdate != curdate:
                for which in ['buy', 'sell']:
                    rate = 0
                    if accum[which]['cur']:
                        rate = accum[which]['usd'] / accum[which]['cur']

                    print("\t{:4} {:6.0f} {:6.2f} {:6.4f} {}".format(which, rate, accum[which]['usd'], accum[which]['cur'], order[4].strftime("%Y-%m-%d")))
                accum = { 'buy': {'usd': 0, 'cur': 0}, 'sell': {'usd': 0, 'cur': 0}}
                print("\t-----")
                curdate = checkdate
            accum[kind]['usd'] += order[2]
            accum[kind]['cur'] += order[3]

            print("\t{:4} {} {:6.2f} {:6.4f} {}".format(kind, order[1], order[2], order[3], order[4].strftime("%Y-%m-%d %H:%M:%S")))


