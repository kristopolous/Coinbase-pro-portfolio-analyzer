#!/usr/bin/python3
import running
import random
import time
import sys
import os
import lib
import tty
import select

currency_list = []
wait = 600
update = 4

margin_buy = 0.09
margin_sell = 0.023
next_act = {}

for i in sys.argv[1:]:
    currency_list.append('BTC_{}'.format(i.upper()))

currency_list = sorted(currency_list)
mod = len(currency_list)
index = 0
ctr = 0
#sys.stderr = open(os.devnull, 'w')
tty.setcbreak(sys.stdin)
while True:
    if index == 0:
        if ctr % 5 == 0:
            print("                                    ")
            print("   ... refreshing data source ...   ")
            print("                                    ")
            lib.returnTicker(forceUpdate = True)
            lib.tradeHistory(forceUpdate = True)
            lib.returnCompleteBalances()
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
        try:
            did_act = running.should_act(currency, margin_buy=margin_buy, margin_sell=margin_sell)
        except:
            did_act = False
            lib.returnTicker(forceUpdate = True)
            lib.tradeHistory(forceUpdate = True)

    if did_act:
        next_act[currency] = time.time() + wait

    if index == 0:
        oldline = ""
        line = ""
        for i in range(update * 20, 0, -1):
            if line != oldline:
                print(line)
                oldline = line

            line = ("\033[0;0H{} {} {:35} {:.3f}{:>" + str(running.graph_len - 5) + "}  {}").format(int(i / 20), time.strftime("%Y-%m-%d %H:%M:%S"), "", margin_buy, "{:.3f}".format(margin_sell), wait)
            time.sleep(1 / 20)
            if select.select([sys.stdin,],[],[],0.0)[0]:
                kc = sys.stdin.read(1)
                if kc == 'w':
                    margin_buy -= 0.001 
                if kc == 'e': 
                    margin_buy += 0.001
                if kc == 's': 
                    margin_sell -= 0.001
                if kc == 'd': 
                    margin_sell += 0.001

                if kc == 'x': 
                    wait -= 5
                    next_act = {k: v - 5 for k,v in next_act.items()}
                if kc == 'c': 
                    wait += 5
                    next_act = {k: v + 5 for k,v in next_act.items()}

                margin_buy = max(margin_buy, 0.0030)
                margin_sell = max(margin_sell, 0.0030)
