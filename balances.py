#!/usr/bin/python3
import sys
import lib
from operator import itemgetter, attrgetter
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument('-l', "--list", action='store_true', help="Show just the currencies")
parser.add_argument('-j', "--json", action='store_true', help="Show a json compatible list")
parser.add_argument('-f', "--force", action='store_true', help="Force update")
args = parser.parse_args()

ticker = lib.returnTicker(forceUpdate = args.force)
cur_balances = lib.returnCompleteBalances()
all_balances = list([(k, float(v['btcValue']), float(v['available']) + float(v['onOrders'])) for k,v in cur_balances.items() ])
all_positive = list(filter(lambda x: x[1] > 0, all_balances))

if args.list:
    print("\n".join(sorted([x[0] for x in all_positive])))
    sys.exit(0)

all_history = lib.tradeHistory()

if args.json:
    list = []
    for k,v in all_history.items():

        row = lib.analyze(v, currency=k, brief=True, sort='date')
        row['exchange'] = k
        cur = k[4:]
        if cur in cur_balances:
            row['bal'] = cur_balances[cur]

        list.append(row)

    print(json.dumps(list))
    sys.exit(0)


market_exit_list = set([ k[4:] for k in all_history.keys() ]) - set([x[0] for x in all_positive])
all_positive = [(v, 0, 0) for v in market_exit_list] + all_positive
in_order = sorted(all_positive, key=itemgetter(1))
btc_ttl = 0

prof_sum = 0
loss_sum = 0
ttl_sum = 0
lib.bprint("{:5} {:>8} {:>8} {:>12} {:>12} {:>12} {:>8}".format( 'cur', 'btc', 'usd', 'prof', 'loss', 'p&l', 'p&l usd'))
for k,b,v in in_order:
    if k != 'BTC':
        market = "BTC_{}".format(k)
        if market not in ticker:
            continue
        history = all_history[market]
        stats = lib.analyze(history, currency=k, brief=True)
        prof = 0
        if stats['buyAvg'] > 0:
            prof = stats['sellCur'] * ( stats['sellAvg'] - stats['buyAvg'] )
            # Based on the current price, we see how far off the breakprice we are
            # and then push it out over our total holdings.
            loss = (ticker[market]['last'] - stats['buyAvg']) * stats['cur']
            ttl = prof + loss
        else:
            continue
    else:
        prof = 0
        loss = 0
        ttl = 0

    btc_ttl += b
    prof_sum += prof
    loss_sum += loss
    ttl_sum += ttl

    lib.bprint("{:5} {:.6f} {:8.2f} {:12.8f} {:12.8f} {:12.8f} {:8.2f}".format( k, b, b * lib.btc_price(), prof, loss, ttl, ttl * lib.btc_price() ))

print("")
lib.bprint(    "{:5} {:.6f} {:8.2f} {:12.8f} {:12.8f} {:12.8f} {:8.2f}".format( 'all', btc_ttl, btc_ttl * lib.btc_price(), prof_sum, loss_sum, ttl_sum, ttl_sum * lib.btc_price()))
