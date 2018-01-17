#!/usr/bin/python3
import secret
import os
import gdax
import hashlib
import json
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
            
            
auth_client = bypass(gdax.AuthenticatedClient(secret.key, secret.b64secret, secret.passphrase))
account_list = auth_client.get_accounts()

history = {}
historySet = set()
def add(exchange, kind, rate, amount, size, date, obj):
    global history
    global historySet
    if exchange not in history:
        history[exchange] = {'buycur':0, 'buyusd':0, 'sellcur':0, 'sellusd':0, 'all': [], 'recent': {'count': 35, 'buycur':0, 'buyusd':0, 'sellcur':0, 'sellusd':0} } 

    if obj['id'] not in historySet:
        historySet.add(obj['id'])
        amount = float(amount)
        if kind == 'buy':
            history[exchange]['buycur'] += amount / float(rate)
            history[exchange]['buyusd'] += amount
            if history[exchange]['recent']['count'] > 0:
                history[exchange]['recent']['buycur'] += amount / float(rate)
                history[exchange]['recent']['buyusd'] += amount
        else:
            history[exchange]['sellcur'] += amount / float(rate) 
            history[exchange]['sellusd'] += amount
            if history[exchange]['recent']['count'] > 0:
                history[exchange]['recent']['sellcur'] += amount / float(rate)
                history[exchange]['recent']['sellusd'] += amount

        history[exchange]['recent']['count'] -= 1
        history[exchange]['all'].append([kind, round(float(rate)), amount, size, parser.parse(date)])

def crawl():
    for account in account_list:
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

                amount = details['executed_value']
                if 'price' in details:
                    rate = details['price']
                else:
                    rate = float(details['executed_value']) / float(details['filled_size'])

                size = float(details['filled_size'])
                add(exchange = details['product_id'], kind = details['side'], amount = amount, date = details['done_at'], size = size, rate = rate, obj=details)

crawl()

for exchange, cur in history.items():
    print(exchange)

    try:
        print("buy:  {:.4f} {:.4f}\nsell: {:.4f} {:.4f}".format(cur['buyusd'] / cur['buycur'], cur['buyusd'], cur['sellusd'] / cur['sellcur'], cur['sellusd']))
        print("buy:  {:.4f} {:.4f}\nsell: {:.4f} {:.4f}".format(cur['recent']['buyusd'] / cur['recent']['buycur'], cur['recent']['buyusd'], cur['recent']['sellusd'] / cur['recent']['sellcur'], cur['recent']['sellusd']))
    except:
        pass
    orderList = reversed(sorted(cur['all'], key=itemgetter(4)))

    for order in orderList:
        print("{:4} {} {:6.2f} {:6.4f} {}".format(order[0], order[1], order[2], 100 * order[3], order[4].strftime("%Y-%m-%d %H:%M:%S")))
