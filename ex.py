#!/usr/bin/python3
from poloniex import Poloniex
import time
import operator
import os
import time
import sys
import secret
p = Poloniex(*secret.token)

#print(p.returnTicker())
hist = {}
step =  86400 * 14 
start = int(time.time()) - (3 * step)

ix = 0
ttl_list = []
ttl = 0
os.system('clear')
while True:

    if ix % 80 == 0:
        all_trades_temp = {}
        ttl_temp = 0
        for i in range(start, int(time.time()), 86400 * 14):
            block_trades = p.returnTradeHistory(start=i, end=i + step)
            if block_trades:
                for k,v in block_trades.items():
                    ttl_temp += len(v)
                    if k not in all_trades_temp:
                        all_trades_temp[k] = []
                    all_trades_temp[k] += v
            time.sleep(1)

        if ttl_temp > ttl:
            ttl = ttl_temp
            all_trades = all_trades_temp

        cur_balances = p.returnBalances()
        all_balances = {k: float(v) for k,v in cur_balances.items() }
        positive_balances = {k: v for k, v in all_balances.items() if v > 0}

        for k in positive_balances.keys():
            key = 'BTC_' + k
            if not key in all_trades:
                continue
            v = all_trades['BTC_' + k]
            bal = 0
            off = 0
            v.reverse()
            for trade in v:
                fee = float(trade['fee'])
                amount = float(trade['total'])
                if trade['type'] == 'buy':
                    bal += amount
                if trade['type'] == 'sell':
                    bal -= amount * (1 - fee)
                #print("{} {} {}".format(trade['date'], k, bal))

    all_prices = p.returnTicker()
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
            btc_ttl1 = btc_ttl + amt
            cur_ttl1 = cur_ttl + amt_cur
            my_price1 = btc_ttl1 / cur_ttl1
            my_ratio1 = price / my_price1
            my_balance1 = my_balance + amt_cur
            #print("{:5} {:0.5f} {:10.5f} {:10.5f} {:10.5f} {:0.8f}".format(cur, btc_ttl, btc_ttl1, cur_ttl, cur_ttl1, price))

            hold1 = (price / (btc_ttl1 / cur_ttl1) - 1) * price * my_balance1
            hold = (my_ratio - 1) * price * my_balance

            rows.append([cur, 1000 * my_price, 1000 * price, my_ratio * 100, 1000 * price * my_balance, 1000 * hold, 10000 * (my_ratio1 / my_ratio) - 10000])


    l = sorted(rows, key=operator.itemgetter(3))

    if len(l)>= len(positive_balances) - 2:
        print("\033[0;0H")
        last_row = 0
        ttl = 0
        row_max = 15
        for row in l:
            if row[3] > 100 and last_row < 100:
                print("-------------------------------------------------------------")
            print("{:5} {:8.5f} {:8.5f} {:7.3f} {:9.5f} {:9.5f} {:9.4f}".format(*row))
            last_row = row[3]
            ttl += row[5]

        ttl_list.append(ttl)
        if len(ttl_list) > 90:
            ttl_list = ttl_list[-90:]

        for x in range(0, row_max):
            row = []
            for y in range(x, len(ttl_list), row_max):
                row.append(ttl_list[y])

            print(' '.join(["{:.5f}".format(l) for l in row]))

    ix += 1
    time.sleep(10)
