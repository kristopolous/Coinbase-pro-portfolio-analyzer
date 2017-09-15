#!/usr/bin/python3
from poloniex import Poloniex
import secret
import lib
from operator import itemgetter, attrgetter
p = Poloniex(*secret.token)

cur_balances = p.returnCompleteBalances()
all_balances = list([(k, float(v['btcValue']), float(v['available']) + float(v['onOrders'])) for k,v in cur_balances.items() ])
all_positive = list(filter(lambda x: x[1] > 0, all_balances))
in_order = sorted(all_positive, key=itemgetter(1))
for k,b,v in in_order:
    if b > 0:
        print("{:6} {:.8f} {:14.8f} {:8.2f}".format( k, b, v, b * lib.btc_price() ))
