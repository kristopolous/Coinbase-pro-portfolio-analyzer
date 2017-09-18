#!/usr/bin/python3
import lib
import sys
import numpy as np
import math
from lib import bprint

currency = False
if len(sys.argv) > 1:
    currency = 'BTC_{}'.format(sys.argv[1].upper())

rows = 15
data = lib.trade_history(currency)
sortlist = sorted(data, key = lambda x: x['rate'])
buyList = list(filter(lambda x: x['type'] == 'buy', sortlist))
sellList = list(filter(lambda x: x['type'] == 'sell', sortlist))

ticker = lib.returnTicker()
last = float(ticker[currency]['last'])
buy_low = buyList[0]['rate']
lowest = min(buy_low, last)
buy_high = max(buyList[-1]['rate'], last)
div = (buy_high - buy_low) / rows

ttl = sum([x['total'] for x in buyList])
grade = ttl / rows / 200

ix = 0
slot_ttl = 0
for slot in np.arange(lowest, buy_high + div, div):
    cprice = ' '
    if last >= slot and last < slot + div:
        cprice = '>'

    if buy_low >= slot and buy_low < slot + div:
        cprice = '^'

    while True:
        if ix >= len(buyList) or buyList[ix]['rate'] > slot:
            break
        slot_ttl += buyList[ix]['total']
        ix += 1

    dots = int(math.sqrt(slot_ttl / grade))
    if slot_ttl > 0 and dots == 0:
        dots = 1

    bprint("{:.7f}{}{}".format(slot, cprice, "".join(["*"] * dots )))
    slot_ttl = 0

lib.recent(currency)
