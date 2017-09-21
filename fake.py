#!/usr/bin/python3
import time
import glob
import csv
import lib
import sys

curlist = []
class Mock:
    def __init__(self):
        self.time = 0
        self.fileMap = {}
        self.ticker = {}

        for path in glob.glob('test/BTC_*'):
            ex = path.split('/')[-1]
            if ex in curlist:
                self.fileMap[ex] = csv.reader(open(path, 'r'))

        self.returnTicker()
        self.time = max(v['date'] for v in self.ticker.values())

    def returnTicker(self):
        for k, v in self.fileMap.items():
            while k not in self.ticker or self.ticker[k]['date'] < self.time:
                x = next(v)
                ticker = {'date': float(x[0]), 'last': float(x[1]) }
                ticker['highestBid'] = ticker['last'] * 0.994
                ticker['lowestAsk'] = ticker['last'] * 1.004
                ticker['percentChange'] = 0
                self.ticker[k] = ticker

                #print(self.time, self.ticker[k]['date'])

        return self.ticker

    def returnCompleteBalances(self):
        if 'balancs' in lib._cache:
            return lib._cache['balances']
        return lib.cache_get('returnCompleteBalances', forceCache = True)

    def returnTradeHistory(self):
        return self.history

    def changeBalance(self, what, amount):
        lib._cache['balances'][what]['available'] += amount

    def trade(self, what, exchange, rate, amount):
        currency = exchange[4:]
        bal = lib._cache['balances'][currency]['available']
        fee = 0.00150000

        total = rate * amount
        btc = total
        cur = amount
        if what == 'sell':
            btc -= total * fee
            if amount > bal:
                return False

            self.changeBalance(currency, -cur)
            self.changeBalance('BTC', btc)

        elif what == 'buy':
            cur -= cur * fee

            self.changeBalance(currency, cur)
            self.changeBalance('BTC', -btc)

        trade = {
          'btc': btc,
          'cur': cur,
          'rate': rate,
          'amount': amount,
          'fee': fee,
          'total': total,
          'type': what
        }

        lib._cache['all_trades'][exchange].append(trade)
        """
        if exchange == 'BTC_STRAT':
            print("{} {}".format(exchange, len(lib._cache['all_trades'][exchange])))
            time.sleep(4)
        """

        return {
          'resultingTrades': [trade]
        }


    def sell(self, exchange, rate, amount):
        return self.trade('sell', exchange, rate, amount)

    def buy(self, exchange, rate, amount):
        return self.trade('buy', exchange, rate, amount)

singleton = False
def connect():
    global singleton
    if not singleton:
        singleton = Mock()
    return singleton

    
