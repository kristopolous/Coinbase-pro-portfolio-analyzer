#!/usr/bin/python3
import lib
import json
import time

cur = lib.getCurrency()
p = lib.connect()
snap = time.time()
book = p.returnOrderBook(depth=40)
book['at'] = snap
print(json.dumps(book))
