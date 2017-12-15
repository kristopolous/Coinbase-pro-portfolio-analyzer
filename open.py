#!/usr/bin/python3
import lib
import sys

currency = False
expiry = 30

priceMap = lib.returnTicker()

if len(sys.argv) > 1:
    currency = 'BTC_{}'.format(sys.argv[1].upper())

if len(sys.argv) > 2:
    expiry = float(sys.argv[2])

def show(what, l, anal = False):
    subset = list(filter(lambda x: x['type'] == what, l))
    if subset:
        lib.bprint(" {:4} {:.8f} {:.8f}".format(what, sum([float(i['total']) for i in subset]), priceMap[currency]['last']))
        for i in subset:
            i['rate'] = float(i['rate'])
            color = '0'
            if what == 'sell':
                if i['rate'] < anal['buyAvg']:
                    color='91'
                elif i['rate'] < anal['break']:
                    color='35'
                elif i['rate'] > max(anal['break'], anal['buyAvg'], anal['sellAvg']):
                    color='32'

            lib.bprint("\x1b[{}m  {} {} {:.8f} {}\x1b[0m".format(color, i['orderNumber'], i['date'], i['rate'], i['total']))

plist = lib.returnOpenOrders(expiry)
history = lib.tradeHistory()

for k,v in plist.items():
    if ((currency and currency == k) or not currency) and len(v):
        print(k)
        show('buy', v)
        anal = lib.analyze(history[k], k)
        show('sell', v, anal)
