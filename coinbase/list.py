#!/usr/bin/python3
import secret
import os
import gdax
import hashlib
import json
import sys
import pdb
import logging
from operator import itemgetter
from dateutil import parser
from decimal import *
getcontext().prec = 2

def hash(*kw):
    return hashlib.md5(json.dumps(kw).encode('utf-8')).hexdigest()

class bypass:
    def __init__(self, real):
        self.real = real

    def clearcache(self, method, args):
       name = "cache/{}".format(hash(method, args))
       if os.path.isfile(name):
           os.remove(name)
       else:
           print("No file: {}".format(name))

    def __getattr__(self, method):
        def cb(*args):
            name = "cache/{}".format(hash(method, args))

            if not os.path.isfile(name):
                data = getattr(self.real, method)(*args)
                with open(name, 'w') as cache:
                    json.dump(data, cache)

            with open(name) as handle:
                return json.loads(handle.read())

        return cb
            
            
def add(exchange, kind, rate, amount, size, date, obj):
    global history
    global historySet

    if exchange not in history:
        history[exchange] = {'buycur':0, 'buyusd':0, 'sellcur':0, 'sellusd':0, 'all': []}
        history[exchange]['recent'] = list(map(lambda x: {'ttl': x, 'sellcount': x, 'buycount': x, 'buycur':0, 'buyusd':0, 'sellcur':0, 'sellusd':0}, range(100, 4000, 250)))

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
        if len(sys.argv) > 1:
            auth_client.clearcache('get_account_history', [account['id']])

        history = auth_client.get_account_history(account['id'])
        for page in range(0,len(history)):
            for order in history[page]:
                try:
                    details = auth_client.get_order(order['details']['order_id'])
                    # print(details)
                except:
                    # print(order)
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
                add(exchange = details['product_id'], kind = details['side'], amount = amount, date = details['done_at'], size = size, rate = rate, obj=details)


logging.basicConfig(level=logging.DEBUG)
auth_client = bypass(gdax.AuthenticatedClient(secret.key, secret.b64secret, secret.passphrase))
account_list = auth_client.get_accounts()
logging.info(account_list)

history = {}
historySet = set()
crawl()

for exchange, cur in history.items():
    print(exchange)

    try:
        print("buy:  {:.2f} {:7.2f} {:.4f}\nsell: {:.2f} {:7.2f} {:.4f}".format(cur['buyusd'] / cur['buycur'], cur['buyusd'], cur['buycur'], cur['sellusd'] / cur['sellcur'], cur['sellusd'], cur['sellcur']))
        for row in cur['recent']:
            buy = 0
            sell = 0
            if row['buycur'] > 0:
                buy = row['buyusd'] / row['buycur']
            if row['sellcur'] > 0:
                sell = row['sellusd'] / row['sellcur']
            print("{:4} buy:  {:.2f} {:.2f} {:.4f} \n     sell: {:.2f} {:.2f}\n".format(row['ttl'], buy, row['buyusd'], 100 * ((sell / buy) - 1), sell, row['sellusd']))
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
            checkdate = order[4].strftime("%Y-%m-%d")
            kind = order[0]
            if checkdate != curdate:
                for which in ['buy', 'sell']:
                    rate = 0
                    if accum[which]['cur']:
                        rate = accum[which]['usd'] / accum[which]['cur']

                    print("{:4} {:6.0f} {:6.2f} {:6.4f} {}".format(which, rate, accum[which]['usd'], accum[which]['cur'], order[4].strftime("%Y-%m-%d")))
                accum = { 'buy': {'usd': 0, 'cur': 0}, 'sell': {'usd': 0, 'cur': 0}}
                print("-----")
                curdate = checkdate
            accum[kind]['usd'] += order[2]
            accum[kind]['cur'] += order[3]

            print("{:4} {} {:6.2f} {:6.4f} {}".format(kind, order[1], order[2], order[3], order[4].strftime("%Y-%m-%d %H:%M:%S")))


