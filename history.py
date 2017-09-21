#!/usr/bin/python3
import lib
import sys
import numpy as np
import math
from lib import bprint

currency = False
if len(sys.argv) > 1:
    currency = 'BTC_{}'.format(sys.argv[1].upper())

"""
graph[low_index] += '\x1b[42m'
if high_index == low_index:
    high_index = min(1 + low_index, graph_len - 1)
graph[high_index] += '\x1b[49m'
"""

rows = 20 
cols = 160
data = lib.tradeHistory(currency)
sortlist = sorted(data, key = lambda x: x['rate'])
buyList = list(filter(lambda x: x['type'] == 'buy', sortlist))
sellList = list(filter(lambda x: x['type'] == 'sell', sortlist))

ticker = lib.returnTicker()
last = float(ticker[currency]['last'])

buy_low = buyList[0]['rate']
buy_high = buyList[-1]['rate']

if len(sellList) > 0:
    sell_low = sellList[0]['rate']
    sell_high = sellList[-1]['rate']
else:
    sell_low = buy_low
    sell_high = buy_high

lowest = min(buy_low, sell_low, last)
highest = max(buy_high, sell_high, last)

div = (highest - lowest) / rows

ttl = sum([x['total'] for x in buyList])
grade = ttl / rows / 400

buy_ix = 0
buy_ttl = 0
sell_ix = 0
sell_ttl = 0
for slot in np.arange(lowest, highest + div, div):
    cprice = ' '
    if last >= slot and last < slot + div:
        cprice = '>'

    if buy_low >= slot and buy_low < slot + div:
        cprice = '^'

    while True:
        if buy_ix >= len(buyList) or buyList[buy_ix]['rate'] > slot:
            break
        buy_ttl += buyList[buy_ix]['total']
        buy_ix += 1

    while True:
        if sell_ix >= len(sellList) or sellList[sell_ix]['rate'] > slot:
            break
        sell_ttl += sellList[sell_ix]['total']
        sell_ix += 1

    dots = min(int(math.sqrt(buy_ttl / grade)), cols)
    if buy_ttl > 0 and dots == 0:
        dots = 1

    row = ["*"] * dots + (cols - dots) * [" "]

    if sell_ttl > 0: 
        row[0] = '\x1b[42m{}'.format(row[0])
        cbar = min(int(math.sqrt(sell_ttl / grade)), cols)
        cbar = max(cbar, 1) 
        row[cbar] = '\x1b[49m{}'.format(row[cbar])

    bprint("{:.7f}{}{}".format(slot, cprice, "".join(row)))
    buy_ttl = 0
    sell_ttl = 0

lib.recent(currency)
