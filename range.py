#!/usr/bin/python3
from poloniex import Poloniex
import time
import operator
import os
import time
import sys
import secret
import math
p = Poloniex(*secret.token)
delta = 0

priceMap = p.returnTicker()
bar = ''
res = 150
low = 0
rows = []

def point(num, char):
    point = int(res * (num - low) / delta)
    bar[point] = char

for k, v in priceMap.items():
    if k[0:3] == 'BTC':
        for i in  ['low24hr', 'lowestAsk', 'last', 'highestBid', 'high24hr', 'baseVolume']:
            v[i] = float(v[i])
        """
        print("{:6} {} {} {} {} {} {}".format( k[4:], 
            v['low24hr'], v['lowestAsk'], v['last'], v['highestBid'], v['high24hr'], v['baseVolume']
        ))
        """ 

        bar = [" " for i in range(0, res)]
        low = v['low24hr'] 
        delta = v['high24hr'] - v['low24hr']
        lowpoint = (v['highestBid'] - low) / delta
        point(v['last'], '*')
        point(v['lowestAsk'], '>')
        point(v['highestBid'], '<')
        bar = "".join(bar)

        rows.append(["{:6} {} {}".format( k[4:], bar, v['baseVolume']), lowpoint])

rows.sort(key = lambda x: x[1])
print("\n".join([k[0] for k in rows]))
