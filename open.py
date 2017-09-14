#!/usr/bin/python3
import lib
import sys

currency = False
if len(sys.argv) > 1:
    currency = 'BTC_{}'.format(sys.argv[1].upper())

def show(what, l):
    subset = list(filter(lambda x: x['type'] == what, l))
    if subset:
        print(what, sum([float(i['total']) for i in subset]))
        for i in subset:
            print(i['date'], i['rate'], i['total'])

p = lib.polo_connect()
plist = p.returnOpenOrders()
for k,v in plist.items():
    if ((currency and currency == k) or not currency) and len(v):
        print(k)
        show('buy', v)
        show('sell', v)
