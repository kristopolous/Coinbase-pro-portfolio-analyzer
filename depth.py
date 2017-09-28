#!/usr/bin/python3
import lib
from pprint import pprint

cur = lib.getCurrency()
p = lib.connect()
pprint(p.returnOrderBook(cur))
