#!/usr/bin/python3
import secret
import os
import gdax
import hashlib
import json
from operator import itemgetter

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
def add(exchange, kind, rate, amount, obj):
    global history
    global historySet
    if exchange not in history:
        history[exchange] = {'buycur':0, 'buyusd':0, 'sellcur':0, 'sellusd':0, 'all':[]}

    if obj['id'] not in historySet:
        historySet.add(obj['id'])
        amount = float(amount)
        if kind == 'buy':
            history[exchange]['buycur'] += amount / float(rate)
            history[exchange]['buyusd'] += amount
        else:
            history[exchange]['sellcur'] += amount / float(rate) 
            history[exchange]['sellusd'] += amount

        history[exchange]['all'].append([kind, float(rate), amount])

def crawl():
    for account in account_list:
        #auth_client.clearcache('get_account_history', [account['id']])
        history = auth_client.get_account_history(account['id'])
        for page in range(0,len(history)):
            for order in history[page]:
                try:
                    details = auth_client.get_order(order['details']['order_id'])
                    #print(details)
                except:
                    # print(order)
                    continue

                amount = details['executed_value']
                if 'price' in details:
                    rate = details['price']
                else:
                    rate = float(details['executed_value']) / float(details['filled_size'])

                add(exchange = details['product_id'], kind = details['side'], amount = amount, rate = rate, obj=details)

crawl()

for exchange, cur in history.items():
    print(exchange)

    print("buy:  {} {}\nsell: {} {}".format(cur['buyusd'] / cur['buycur'], cur['buyusd'], cur['sellusd'] / cur['sellcur'], cur['sellusd']))
    orderList = sorted(cur['all'], key=itemgetter(1))

    """ 
    for order in orderList:
        print(order)
    """
