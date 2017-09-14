#!/usr/bin/python3
import lib
import sys

def show(what, l):
    subset = list(filter(lambda x: x['type'] == what, l))
    if subset:
        print(what, sum([float(i['total']) for i in subset]))
        for i in subset:
            print(i['date'], i['rate'], i['total'])

p = lib.polo_connect()
plist = p.returnOpenOrders()
for k,v in plist.items():
    if len(v):
        print(k)
        show('buy', v)
        show('sell', v)
