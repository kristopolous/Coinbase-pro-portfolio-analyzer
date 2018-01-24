#!/usr/bin/python3
import lib
import sys
from operator import itemgetter, attrgetter

currency = False
if len(sys.argv) > 1:
    currency = 'BTC_{}'.format(sys.argv[1].upper())

hist  = lib.trade_history(currency)
ttl_btc = 0
ttl_cur = 0
recent = []

for row in hist:
    if row['type'] == 'buy':
        ttl_btc -= row['btc']
        ttl_cur += row['cur']
    if row['type'] == 'sell':
        ttl_btc += row['btc']
        ttl_cur -= row['cur']

    # if we've exited the currency then we reset our
    # counters
    if ttl_cur < 0.0000000001:
        print("{} {:7f}".format(row['date'], ttl_btc))
        ttl_btc = 0
        recent = []
    else:
        recent.append(row)

    print("{} {:.7f} {:.20f} {:.7f}".format(row['date'], ttl_btc, ttl_cur, row['total']))

"""
def show(what, l):
    subset = list(filter(lambda x: x['type'] == what, l))
    if subset:
        print(" {:4} {:.8f}".format(what, sum([float(i['total']) for i in subset])))
        for i in subset:
            print("  {} {} {} {}".format(i['orderNumber'], i['date'], i['rate'], i['total']))

plist = lib.returnOpenOrders()

for k,v in plist.items():
    if ((currency and currency == k) or not currency) and len(v):
        print(k)
        show('buy', v)
        show('sell', v)
"""
