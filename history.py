#!/usr/bin/python3
import lib
import sys
import numpy as np
import math
from lib import bprint

cur = False
currency = False
margin = False
if len(sys.argv) > 1:
    cur = sys.argv[1].upper()
    currency = 'BTC_{}'.format(cur)

if len(sys.argv) > 2:
    margin = float(sys.argv[2])

"""
graph[low_index] += '\x1b[42m'
if high_index == low_index:
    high_index = min(1 + low_index, graph_len - 1)
graph[high_index] += '\x1b[49m'
"""

rows = 80 
cols = 150
data = lib.tradeHistory(currency)
anal = lib.analyze(data)
balanceMap = lib.returnCompleteBalances()
sortlist = sorted(data, key = lambda x: x['rate'])
buyList = anal['buyList']
sellList = anal['sellList']

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

if margin:
    midpoint = (highest + lowest) / 2 
    lowest = midpoint * (100 - margin) / 100
    highest = midpoint * (100 + margin) / 100

div = (highest - lowest) / rows

ttl = sum([x['total'] for x in buyList])
grade = ttl / rows / 8

buy_ix = 0
buy_ttl = 0
sell_ix = 0
sell_ttl = 0

lib.bprint("{:10} {}\n".format(currency, balanceMap[cur]['btcValue']))
 
slot = lowest
while slot <  highest + 2*div:
    slot_line = "{:.8f} ".format(slot)
    if last >= slot and last <= slot + div:
        slot_line = "\x1b[44m\x1b[37;1m{}\x1b[0m".format(slot_line)

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

    dots = min(int((buy_ttl / grade)), cols - 1)
    if buy_ttl > 0 and dots == 0:
        dots = 1

    row = ["\u2590"] * dots + (cols - dots) * [" "]

    if sell_ttl > 0: 
        row[0] = '\x1b[42m{}'.format(row[0])
        cbar = min(int((sell_ttl / grade)), cols - 1)
        cbar = max(cbar, 1) 
        row[cbar] = '\x1b[49m{}'.format(row[cbar])

    row[0] = '\x1b[35m' + row[0]
    row[-1] += '\x1b[0m'

    bprint("{}{}".format(slot_line, "".join(row)))
    buy_ttl = 0
    sell_ttl = 0
    div *= 1.04
    slot += div

lib.recent(currency)
