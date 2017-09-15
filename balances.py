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
btc_ttl = 0

for k,b,v in in_order:
    if b > 0:
        btc_ttl += b
        print("{:6} {:.8f} {:8.2f} {:14.8f}".format( k, b, b * lib.btc_price(), v ))

print("--------------------------")
print("{:6} {:.8f} {:8.2f}".format( 'all', btc_ttl, btc_ttl * lib.btc_price() ))
