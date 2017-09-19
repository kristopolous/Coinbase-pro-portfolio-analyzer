#!/usr/bin/python3
import running
import random
import time
import sys
import lib

currency_list = []
wait = 240
margin = 0.05

for i in sys.argv[1:]:
    currency_list.append('BTC_{}'.format(i.upper()))

random.shuffle(currency_list)
mod = len(currency_list)
index = 0

while True:
    currency = currency_list[index]
    index = (index + 1) % mod 

    try:
        did_act = running.should_act(currency, margin=margin)
    except:
        lib.plog("{} Threw an error".format(currency))
        did_act = False

    if did_act:
        time.sleep(wait) 
    else:
        time.sleep(wait / 20)
