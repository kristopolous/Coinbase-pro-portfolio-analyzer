#!/usr/bin/python3
import lib
import sys
from lib import bprint
from operator import itemgetter, attrgetter

cur = False
currency = False
margin = False
if len(sys.argv) > 1:
    cur = sys.argv[1].upper()
    currency = 'BTC_{}'.format(cur)

if len(sys.argv) > 2:
    margin = float(sys.argv[2])

rows = 80 
cols = 150
data = lib.tradeHistory(currency)
anal = lib.analyze(data)
balanceMap = lib.returnCompleteBalances()
ticker = lib.returnTicker()

buyList = anal['buyList']
sellList = anal['sellList']

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

buy_ix = 0
buy_ttl = 0
sell_ix = 0
sell_ttl = 0

lib.bprint("{:10} {}\n".format(currency, balanceMap[cur]['btcValue']))
 
buyMap = {}
slot = lowest
div_orig = div
while slot <  highest + 2*div:
    buy_ttl = 0
    div *= 1.04
    while True:
        if buy_ix >= len(buyList) or buyList[buy_ix]['rate'] > (slot + div):
            break
        buy_ttl += buyList[buy_ix]['total']
        buy_ix += 1

    buyMap[slot] = buy_ttl
    slot += div

buy_max = max(buyMap.values())
buy_ttl = 0
div = div_orig

slot = lowest
scale = lowest * 1.5
while slot <  highest + 2*div:
    slot_line = " {:.8f} ".format(slot)

    if slot > scale:
        scale *= 1.5
        slot_line = '*' + slot_line[1:]

    div *= 1.04
    if last >= slot and last <= slot + div:
        slot_line = "\x1b[44m\x1b[37;1m{}\x1b[0m".format(slot_line)

    buy_ttl = buyMap[slot]

    while True:
        if sell_ix >= len(sellList) or sellList[sell_ix]['rate'] > (slot + div):
            break
        sell_ttl += sellList[sell_ix]['total']
        sell_ix += 1

    dots = min(int(cols * (buy_ttl / buy_max)), cols - 1)
    if buy_ttl > 0 and dots == 0:
        dots = 1

    row = ["\u2590"] * dots + (cols - dots) * [" "]

    if sell_ttl > 0: 
        row[0] = '\x1b[42m{}'.format(row[0])
        cbar = min(int(cols * (sell_ttl / buy_max)), cols - 1)
        cbar = max(cbar, 1) 
        row[cbar] = '\x1b[49m{}'.format(row[cbar])

    row[0] = '\x1b[35m' + row[0]
    row[-1] += '\x1b[0m'

    bprint("{}{}".format(slot_line, "".join(row)))
    sell_ttl = 0
    slot += div

anal['buyList'] = sorted(anal['buyList'], key=itemgetter('date'))
anal['sellList'] = sorted(anal['sellList'], key=itemgetter('date'))

lib.recent(currency, anal)
