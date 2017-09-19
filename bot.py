#!/usr/bin/python3
import running
import random
import time
import sys

currency_list = []
wait = 240

for i in sys.argv[1:]:
    currency_list.append('BTC_{}'.format(i.upper()))

random.shuffle(currency_list)
mod = len(currency_list)
index = 0

while True:
    currency = currency_list[index]
    index = (index + 1) % mod 

    row = []
    for i in currency_list:
        row.append(" {}{}".format('*' if currency == i else ' ', i))

    print("{} {}".format(time.strftime("%Y-%m-%d %H:%M:%S"), "".join(row)))
    try:
        did_act = running.should_act(currency, margin=0.08)
    except:
        print("Threw an error")
        did_act = False

    if not did_act:
        my_wait = wait / 20
        delay = my_wait / 2
    else:
        my_wait = wait
        delay = my_wait / 3
    for i in range(round(my_wait / delay), 0, -1):
        print("{:4d} {}".format(i, time.strftime("%Y-%m-%d %H:%M:%S")))
        time.sleep(delay)
