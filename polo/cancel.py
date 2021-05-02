#!/usr/bin/python3
import lib
import json
import sys

p = lib.connect()
for i in sys.argv[1:]:
    print("{} {}".format(i, p.cancelOrder(i)))
