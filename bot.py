#!/usr/bin/python3
import running
import random
import time
import sys
import os
import lib

currency_list = []
wait = 600
update = 7

margin_buy = 0.05
margin_sell = 0.02
next_act = {}

for i in sys.argv[1:]:
    currency_list.append('BTC_{}'.format(i.upper()))

currency_list = sorted(currency_list)
mod = len(currency_list)
index = 0
ctr = 0
#sys.stderr = open(os.devnull, 'w')
while True:
    if index == 0:
        lib.returnTicker(forceUpdate = True)
        lib.tradeHistory(forceUpdate = True)
        lib.returnCompleteBalances()
        if ctr % 5 == 0:
            os.system('clear')
            print("")
        ctr += 1

    currency = currency_list[index]
    index = (index + 1) % mod 

    if currency in next_act:
        if time.time() > next_act[currency]:
            del(next_act[currency])
        else:
            running.please_skip(currency, margin_buy=margin_buy, margin_sell=margin_sell, extra=int(next_act[currency] - time.time()))

    if not currency in next_act:
        did_act = running.should_act(currency, margin_buy=margin_buy, margin_sell=margin_sell)

    if did_act:
        next_act[currency] = time.time() + wait

    if index == 0:
        for i in range(update, 0, -1):
            print("\033[0;0Hmargin: {}/{} wait: {} {} {} ".format(margin_buy, margin_sell, wait, i, time.strftime("%Y-%m-%d %H:%M:%S")))
            time.sleep(1)
