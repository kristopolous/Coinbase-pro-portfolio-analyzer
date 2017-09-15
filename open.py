#!/usr/bin/python3
import lib
import json
import sys

currency = False
if len(sys.argv) > 1:
    currency = 'BTC_{}'.format(sys.argv[1].upper())

def show(what, l):
    subset = list(filter(lambda x: x['type'] == what, l))
    if subset:
        print(" {:4} {:.8f}".format(what, sum([float(i['total']) for i in subset])))
        for i in subset:
            print("  {} {} {} {}".format(i['orderNumber'], i['date'], i['rate'], i['total']))

if lib.need_to_get('cache/open', expiry=240):
   with open('cache/open', 'w') as cache:
       p = lib.polo_connect()
       plist = p.returnOpenOrders()
       json.dump(plist, cache)

with open('cache/open') as json_data:
    plist = json.load(json_data)

for k,v in plist.items():
    if ((currency and currency == k) or not currency) and len(v):
        print(k)
        show('buy', v)
        show('sell', v)
