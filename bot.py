#!/usr/bin/python3
import running
import time
import sys

currency_list = []
wait = 300

for i in sys.argv[1:]:
    currency_list.append('BTC_{}'.format(i.upper()))

mod = len(currency_list)
index = 0

while True:
    currency = currency_list[index]
    index = (index + 1) % mod 

    row = []
    for i in currency_list:
        row.append("{}{}".format('*' if currency == i else ' ', i))

    print("{} {}".format(time.strftime("%Y-%m-%d %H:%M:%S"), "".join(row)))
    running.should_act(currency, margin=0.08)

    delay = wait / 45
    for i in range(round(wait / delay), 0, -1):
        print("{:4d} {}".format(i, time.strftime("%Y-%m-%d %H:%M:%S")))
        time.sleep(delay)
