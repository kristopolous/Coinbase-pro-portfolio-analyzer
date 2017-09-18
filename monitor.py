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
os.system('clear')

rowOrderList = [
    [ 'cur', '{:5}', '{:5}'],
    [ 'buy', '{:>9}', '{:9.4f}'],
    [ 'avgbuy', '{:>8}', '{:8.5f}'],
    [ 'price', '{:>8}', '{:8.5f}'],
    [ 'roi', '{:>7}', '{:7.3f}'],
    [ 'bal', '{:>8}', '{:8.3f}'],
    [ 'prof', '{:>8}', '{:8.3f}'],
    [ 'sell', '{:>9}', '{:9.4f}'],
    [ 'delta','{:>9}', '{:9.4f}']
]

while True:

    if ix % 80 == 0:
        all_trades = lib.trade_history('all')

        cur_balances = lib.returnCompleteBalances()
        all_balances = {k: float(v['available']) + float(v['onOrders']) for k,v in cur_balances.items() }
        positive_balances = {k: v for k, v in all_balances.items() if v > 0.0001}

        for k, v in all_trades.items():
            all_trades[k] = lib.ignorePriorExits(v)


    all_prices = p.returnTicker()
    with open('cache/ticker', 'w') as ticker:
        json.dump(all_prices, ticker)

    rows = []

    for k,v in all_trades.items():
        buys = list(filter(lambda x: x['type'] == 'buy', v))
        btc_ttl = sum([float(t['total']) for t in buys])
        cur_ttl = sum([float(t['amount']) * (1 - float(t['fee'])) for t in buys])
        price = float(all_prices[k]['last'])
        if k[:3] == 'ETH' or cur_ttl == 0: 
            continue
        my_price = btc_ttl / cur_ttl 
        my_ratio = price / my_price
        cur = k[4:]
        if cur in positive_balances:
            my_balance = float(positive_balances[cur])

            amt = 0.00010001
            amt_cur = ((1-0.0025) * amt) / price

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

            hold = (my_ratio - 1) * price * my_balance

            rows.append({
                'cur': cur, 
                'avgbuy': 1000 * my_price, 
                'price': 1000 * price, 
                'roi': my_ratio * 100, 
                'bal': lib.btc_price() * price * my_balance, 
                'prof': lib.btc_price() * hold, 
                'buy': 10000 * (my_ratio_buy / my_ratio) - 10000,
                'sell': 10000 * (my_ratio_sell / my_ratio) - 10000,
                'delta': 100 * math.pow(abs(((my_ratio_buy / my_ratio) - 1) / ((my_ratio_sell / my_ratio) - 1)), 5)
            })

    l = sorted(rows, key=operator.itemgetter('roi'))
    
    if ix % 10 == 0:
        os.system('clear')
    print("\033[0;0H")
    last_row = 0
    ttl = 0
    row_max = 10
    header = []
    for column in rowOrderList:
        header.append(column[1].format(column[0]))
    header = " ".join(header)
    rowlen = len(header)
    print(header)

    for row in l:
        if row['roi'] > 100 and last_row < 100:
            print("-" * rowlen)

        output = []
        for column in rowOrderList:
            output.append(column[2].format(row[column[0]]))
        print(" ".join(output))

        last_row = row['roi']
        ttl += row['prof']

    ttl_list.append(ttl)
    if len(ttl_list) > 120:
        ttl_list = ttl_list[-120:]

    for x in range(0, row_max):
        row = []
        for y in range(x, len(ttl_list), row_max):
            row.append(ttl_list[y])

        print(' '.join(["{:.5f}".format(l) for l in row]))

    ix += 1
    time.sleep(10)
