#!/usr/bin/python3
import running
import random
import time
import sys
import lib

currency_list = []
wait = 210
margin = 0.06

for i in sys.argv[1:]:
    currency_list.append('BTC_{}'.format(i.upper()))

random.shuffle(currency_list)
mod = len(currency_list)
index = 0

while True:
    if index == 0:
        print("margin: {}".format(margin))
    currency = currency_list[index]
    index = (index + 1) % mod 

    did_act = running.should_act(currency, margin=margin)

    if did_act:
        time.sleep(wait) 
    else:
        time.sleep(wait / 50)
