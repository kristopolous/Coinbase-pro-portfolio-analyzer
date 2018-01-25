#!/usr/bin/python3
import lib
import sys
from pprint import pprint

all_history = lib.tradeHistory()
balanceMap = lib.returnCompleteBalances()

for k,v in all_history.items():
    print(k)

    #v = lib.analyze(v, currency=k, brief=True, sort='date')
    v = lib.analyze(v, currency=k, brief=True, sort='date')

    cur = k[4:]
    if cur in balanceMap:
        v['bal'] = balanceMap[cur]
    pprint(v)
