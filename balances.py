#!/usr/bin/python3
from poloniex import Poloniex
import secret
import lib
from operator import itemgetter, attrgetter
p = Poloniex(*secret.token)

all_history = lib.tradeHistory()
cur_balances = p.returnCompleteBalances()
all_balances = list([(k, float(v['btcValue']), float(v['available']) + float(v['onOrders'])) for k,v in cur_balances.items() ])
all_positive = list(filter(lambda x: x[1] > 0, all_balances))
market_exit_list = set([ k[4:] for k in all_history.keys() ]) - set([x[0] for x in all_positive])
all_positive = [(v, 0, 0) for v in market_exit_list] + all_positive
in_order = sorted(all_positive, key=itemgetter(1))
btc_ttl = 0

prof_sum = 0
for k,b,v in in_order:
    if k != 'BTC':
        history = all_history["BTC_{}".format(k)]
        stats = lib.analyze(history, brief=True)
        prof = 0
        if stats['avgBuy'] > 0:
            prof = stats['sellBtc'] * ( stats['avgSell'] / stats['avgBuy']  - 1)
        else:
            continue
    else:
        prof = 0

    btc_ttl += b
    prof_sum += prof

    lib.bprint("{:6} {:.8f} {:8.2f} {:14.8f} {:14.8f} {:8.2f}".format( k, b, b * lib.btc_price(), v, prof, prof * lib.btc_price() ))

print("--------------------------")
lib.bprint("{:6} {:.8f} {:8.2f} {:14} {:14.8f} {:8.2f}".format( 'all', btc_ttl, btc_ttl * lib.btc_price(), "", prof_sum, prof_sum * lib.btc_price()))
