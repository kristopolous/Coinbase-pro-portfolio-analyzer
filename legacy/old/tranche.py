#!/usr/bin/python3
import time
import sys
import json
import os
import lib

currency = 'BTC_STRAT'

if len(sys.argv) > 1:
    currency = 'BTC_{}'.format(sys.argv[1].upper())

profit = 0.05
fee = 0.0025
hist = {}


def tally_print(tally):
    buy_at = tally['break'] * (1 - (profit - fee) / 2)
    sell_at = tally['break'] * (1 + (profit - fee) / 2)

    print("{:.10f} ({:.10f}-{:.10f}) b{:.10f} buy:{:.10f} sell:{:.10f} ({})".format(tally['break'], tally['low'], tally['high'], -tally['btc'], buy_at, sell_at, tally['len']))

def process(tradeList):
    for i in range(0, len(tradeList)):
        tradeList[i]['total'] = float(tradeList[i]['total'])
        tradeList[i]['amount'] = float(tradeList[i]['amount'])
        tradeList[i]['rate'] = float(tradeList[i]['rate'])
        tradeList[i]['fee'] = float(tradeList[i]['fee'])

def tally(tradeList):
    btc = 0
    cur = 0
    cur_low = 1000000 
    cur_high = 0
    max_btc_invested = 0
    for trade in tradeList:
        if trade['type'] == 'buy':
            btc -= trade['total']
            cur += trade['amount']
        if trade['type'] == 'sell':
            btc += trade['total']
            cur -= trade['amount']

        cur_low = min(cur_low, trade['rate'])
        cur_high = max(cur_high, trade['rate'])
        max_btc_invested = max(max_btc_invested, -btc)

    break_even = -btc / cur
    return {'break': break_even, 'low': cur_low, 'high': cur_high, 'max_btc_invested': max_btc_invested, 'btc': btc, 'cur': cur, 'len': len(tradeList)}

print("{} {}".format(currency, profit))
data = lib.tradeHistory(currency)
process(data)
ttl = tally(data)

sortlist = sorted(data, key = lambda x: x['rate'])
# 
# We want to equally weight the tranches based on currently 
# outstanding investments. 
#
# So we sort the trades based on price and then run through them
# until we get to a breakpoint (currently outstanding / group size)
# 
groups = 6 
threshold = abs(ttl['btc'] / groups)

tranche = []
btc = 0
for trade in sortlist:
    if trade['type'] == 'buy':
        btc += trade['total']
    else:
        btc -= trade['total']

    if btc > threshold:
        # break the trade up

        # This amount goes into this tranche
        partial_total = threshold - (btc - trade['total'])

        # We need to get the fractional amount
        frac = partial_total / trade['total']

        # now we make a "fake" trade with the partial
        fake_trade = {
            'type': 'buy',
            'total': partial_total,
            'rate': trade['rate'],
            'fee': trade['fee'] * frac,
            'amount': trade['amount'] * frac
        }
        tranche.append(fake_trade)

        trade['total'] -= partial_total
        trade['fee'] -= fake_trade['fee']
        trade['amount'] -= fake_trade['amount']
            
        agg = tally(tranche)
        tally_print(agg)


        tranche = []
        btc = 0
    tranche.append(trade)


if len(tranche) > 0:
    agg = tally(tranche)
    tally_print(agg)


def distrib():
    trade_chunk = int(len(data) / groups)
    #buy_list = list(filter(lambda x: x['type'] == 'buy', data))

    tranche_list = []
    for i in range(0, len(data), trade_chunk):
        tranche = tlist[i:i + trade_chunk]
        agg = tally(tranche)
        tranche_list.append(agg)
        #print("{} {}".format(i, i + trade_chunk))
        tally_print(agg)

print(len(data))
