#!/usr/bin/python3
import running
import random
import time
import sys
import os
import lib
import tty
import select
import fake
import json

currency_list = []
wait_before_next_trade = 300
ui_update = 3
cycles_before_data_update = 20

margin_buy = 0.015
margin_sell = 0.015
subtime = 20
next_act = {}


for i in sys.argv[1:]:
    currency_list.append('BTC_{}'.format(i.upper()))

if 'BOT_FAKE' in os.environ:
    lib.is_fake = True
    fake.curlist =  currency_list
    subtime = 1
elif 'BOT_REAL' in os.environ:
    lib.is_fake = False
else:
    print("Need to either set BOT_FAKE or BOT_REAL environ variables to run this. Bye bye")
    sys.exit(-1)

currency_list = sorted(currency_list)
mod = len(currency_list)
index = 0
ctr = 0
#sys.stderr = open(os.devnull, 'w')
tty.setcbreak(sys.stdin)

anal = open('anal', 'w')

print("\033?25l")
os.system('clear')
while True:
    if index == 0:
        if ctr % cycles_before_data_update == 0:
            if not lib.is_fake:
                print("                                    ")
                print("   ... refreshing data source ...   ")
                print("                                    ")
            ticker = lib.returnTicker(forceUpdate = True)
            trades = lib.tradeHistory(forceUpdate = True)
            all_bal = lib.returnCompleteBalances()

            if not lib.is_fake:
                os.system('clear')
            print("\033[0;0H")
            stats = lib.analyze(lib.tradeHistory('BTC_STRAT'), brief = True)
            anal.write("{} {}\n".format(stats['avgBuy'], stats['btc']))
        ctr += 1

    currency = currency_list[index]
    index = (index + 1) % mod 

    did_act = False
    if currency in next_act:
        if lib.unixtime() > next_act[currency]:
            del(next_act[currency])
        else:
            running.please_skip(currency, margin_buy=margin_buy, margin_sell=margin_sell, extra=int(next_act[currency] - lib.unixtime()))

    if not currency in next_act:
        #try:
        did_act = running.should_act(currency, margin_buy=margin_buy, margin_sell=margin_sell)
        """
        except:
            did_act = False
            lib.returnTicker(forceUpdate = True)
            lib.tradeHistory(forceUpdate = True)
        """

    if did_act:
        next_act[currency] = lib.unixtime() + wait_before_next_trade

    if index == 0:
        oldline = ""
        line = ""
        for i in range(max(ui_update * subtime, 1), 0, -1):
            if line != oldline:
                print(line)
                oldline = line

            line = ("\033[0;0H {} {:35} {:.3f}{:>" + str(running.graph_len - 5) + "}  {}").format( time.strftime("%Y-%m-%d %H:%M:%S", lib.now()), "", margin_buy, "{:.3f}".format(margin_sell), wait_before_next_trade)
            lib.wait(1 / subtime)

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
                    wait_before_next_trade -= 5
                    next_act = {k: v - 5 for k,v in next_act.items()}
                if kc == 'c': 
                    wait_before_next_trade += 5
                    next_act = {k: v + 5 for k,v in next_act.items()}

                margin_buy = max(margin_buy, 0.0030)
                margin_sell = max(margin_sell, 0.0030)
