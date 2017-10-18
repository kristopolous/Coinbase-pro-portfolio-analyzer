#!/usr/bin/python3
from poloniex import Poloniex
import time
import operator
import os
import time
import sys
import secret
import math
import lib
import json
p = Poloniex(*secret.token)

ix = 0
ttl_list = []
ttl = 0
all_prices_last_list = False
all_prices_last = False

waitTime = 9 
tradeUpdate = 900
row_max = 15
col_max = 15
start_time = time.time()

tradeUpdate = round(tradeUpdate / waitTime)

os.system('clear')

rowOrderList = [
    [ 'cur', '{:5}', '{:5}'],
    [ 'mvlng', '{:>7}', '{:7.3f}'],
    [ 'mvmed', '{:>7}', '{:7.3f}'],
    [ 'mvsrt', '{:>7}', '{:7.3f}'],
    [ '24h', '{:>7}', '{:7.2f}'],
    [ 'price', '{:>8}', '{:8.5f}'],
    [ 'last', '{:>9}', '{}'],
    [ 'brk', '{:>8}', '{:8.5f}'],
    [ 'bprof', '{:>7}', '{:7.2f}'],
    [ 'roi', '{:>7}', '{:7.2f}'],
    [ 'bal', '{:>8}', '{:8.3f}'],
    [ 'prof', '{:>8}', '{:8.3f}']
]

while True:

    last_update = time.time()
    if ix % tradeUpdate == 0:
        all_trades = lib.tradeHistory('all')
        last_portfolio = time.strftime("%Y-%m-%d %H:%M:%S")

        cur_balances = {k: v for k, v in lib.returnCompleteBalances().items() if v['btcValue'] > 0.0001}
        positive_balances = {k: v['cur'] for k,v in cur_balances.items() }

        for k, v in all_trades.items():
            all_trades[k] = {
                'full': v,
                'last': lib.ignorePriorExits(v)
            }


    all_prices = lib.returnTicker(forceUpdate = True)
    last_ticker = time.strftime("%Y-%m-%d %H:%M:%S")
    if not all_prices_last:
        all_prices_last = [all_prices] * 3
        all_prices_last_list = [all_prices]

    rows = []

    for k,valueMap in all_trades.items():
        v = valueMap['last']
        statsFull = lib.analyze(valueMap['full'], currency=k, brief=True)
        stats = lib.analyze(valueMap['last'], currency=k, brief=True)
        btc_ttl = stats['buyBtc']
        btc_ttl_sell = stats['sellBtc']

        cur_ttl = stats['buyCur']
        price = float(all_prices[k]['last'])
        if k[:3] == 'ETH' or cur_ttl == 0: 
            continue
        my_price = btc_ttl / cur_ttl 
        my_ratio = min(price / my_price, price / statsFull['buyAvg'])
        cur = k[4:]
        if cur in positive_balances:
            my_balance = float(positive_balances[cur])

            amt = lib.MIN
            amt_cur = ((1 - 0.0025) * amt) / price

            btc_ttl_buy = btc_ttl + amt
            cur_ttl_buy = cur_ttl + amt_cur
            my_price_buy = btc_ttl_buy / cur_ttl_buy
            my_ratio_buy = price / my_price_buy
            my_balance_buy = my_balance + amt_cur

            btc_ttl_sell = btc_ttl - amt
            cur_ttl_sell = cur_ttl - amt_cur
            my_price_sell = btc_ttl_sell / cur_ttl_sell
            my_ratio_sell = price / my_price_sell
            my_balance_sell = my_balance - amt_cur
            #print("{:5} {:0.5f} {:10.5f} {:10.5f} {:10.5f} {:0.8f}".format(cur, btc_ttl, btc_ttl1, cur_ttl, cur_ttl1, price))

            hold_buy = (price / (btc_ttl_buy / cur_ttl_buy) - 1) * price * my_balance_buy
            hold_sell = (price / (btc_ttl_sell / cur_ttl_sell) - 1) * price * my_balance_sell

            hold = (price / stats['break'] - 1) * price * my_balance

            break_price = 1000.0 * stats['break']
            bprof = 0
            if break_price > 0:
               bprof = (100000 * (price / break_price)) - 100
            else:
               break_price = 0

            rows.append({
                'cur': cur, 
                'last': "{:8.5f}{}".format(v[-1]['rate'] * 1000, '*' if v[-1]['type'][0] == 'b' else ' '),
                'price': 1000 * price, 
                'roi': my_ratio * 100 - 100, 
                '24h': all_prices[k]['percentChange'] * 100,
                'bal': lib.btc_price() * price * my_balance, 
                'prof': lib.btc_price() * hold, 
                'brk': break_price,
                'bprof': bprof,
                'buy': 10000 * (my_ratio_buy / my_ratio) - 10000,
                'sell': 10000 * (my_ratio_sell / my_ratio) - 10000,
                'mvlng': 100 - (100 * all_prices_last[0][k]['last'] / all_prices[k]['last']),
                'mvmed': 100 - (100 * all_prices_last[1][k]['last'] / all_prices[k]['last']),
                'mvsrt': 100 - (100 * all_prices_last[2][k]['last'] / all_prices[k]['last']),
                'to': 100 * math.pow(abs(((my_ratio_buy / my_ratio) - 1) / ((my_ratio_sell / my_ratio) - 1)), 5)
            })

    l = sorted(rows, key=operator.itemgetter('roi'))
    
    if ix % 10 == 0:
        os.system('clear')
    print("\033[0;0H  0 price:{} | portfolio:{}".format(time.strftime("%Y-%m-%d %H:%M:%S"), last_portfolio))
    last_row = 0
    ttl = 0
    header = []
    for column in rowOrderList:
        header.append(column[1].format(column[0]))
    header = " ".join(header)
    rowlen = len(header)
    print(header)
    didBar = False

    for row in l:
        if row['roi'] > 0 and last_row < 0:
            print("-" * rowlen)
            didBar = True

        output = []
        for column in rowOrderList:
            output.append(lib.bstr(column[2].format(row[column[0]])))
        print(" ".join(output))

        last_row = row['roi']
        ttl += row['prof']

    if not didBar:
        print("-" * rowlen)

    if ix > (12 * (row_max - 1)):
       all_prices_last_list.pop(0)

    mindex = len(all_prices_last_list) - 1
    all_prices_last = [
       all_prices_last_list[0],
       all_prices_last_list[int(1/2 * mindex)],
       all_prices_last_list[int(3/4 * mindex)]
    ]
    all_prices_last_list.append(all_prices)

    if ix % (row_max - 1) == 0:
        ttl_list.append("{:>8}".format(time.strftime("%H:%M")))
        ttl_base = ttl
        ttl_list.append("{:>8}".format("{:.2f}".format(ttl)))


    else:
        toadd = lib.bstr("{:>8}".format("{:.4f}".format(100 - (100 * ttl / ttl_base))))
        ttl_list.append(toadd)


    if len(ttl_list) > (row_max * col_max):
        ttl_list = ttl_list[-(row_max * col_max):]

    for x in range(0, row_max):
        row = []
        for y in range(x, len(ttl_list), row_max):
            row.append(ttl_list[y])

        print(' '.join(row))

    ix += 1

    # might as well be delay accurate as if it matters (it doesn't)
    waitfor = max(start_time + ix * waitTime - time.time(), 4)
    precision = 10 
    for i in range(round(waitfor * precision), 0, -1):
        print("\033[0;0H{:3.0f} price:{} | portfolio:{}".format(i / precision, last_ticker, last_portfolio))
        time.sleep(1 / precision)

