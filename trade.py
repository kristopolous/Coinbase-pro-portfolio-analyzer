#!/usr/bin/python3
from poloniex import Poloniex
import json
import sys
import time
import secret
import argparse
import lib
import re

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--currency", required=True, help="Currency to buy")
parser.add_argument('-a', "--action", required=True, help="Action, either buy or sell")
parser.add_argument('-q', "--quantity", default=0, help="Quantity to buy, expressed in btc (also 'min' for minimum amount)")
parser.add_argument('-r', "--rate", default=None, help="Rate (defaults to market). Also accepts lowest, highest,break, profit, ask, bid, and percent. Also math can be done. Such as profit+0.2%")
parser.add_argument('-n', "--nofee", action='store_true', help="Try to avoid the higher fee")
parser.add_argument('-f', "--fast", action='store_true', help="Skip the ceremony and do things quickly")
args = parser.parse_args()

p = Poloniex(*secret.token)

currency = args.currency.upper()
exchange = 'BTC_{}'.format(currency)

satoshi = 1e-8

if args.quantity == 'min':
    args.quantity = str(lib.MIN)

quantity = float(args.quantity.replace('_', '0'))
rate = args.rate

if rate:
    rate = rate.replace('_', '0')

action = args.action.lower()
fast = args.fast
lowest = False
spreadThreshold = 0.005

# This is only used for the warning message to make sure
# the fingers don't slip and someone buys/sells the farm
# (say by leaving out a decimal point)
#
# curl https://api.coindesk.com/v1/bpi/currentprice.json
#
approx_btc_usd = lib.btc_price()

# let's set it really low for now. 
warn_at_usd = 3.50

def warn(msg):
    lib.bprint("\nWARNING:\n {}\n\n".format(msg.replace('\n', '\n ')))


def abort(msg):
    print("\nERROR:\n {}\n\n Aborted.".format(msg.replace('\n', '\n ')))
    sys.exit(-1)

if quantity > (warn_at_usd / approx_btc_usd):
    usd = approx_btc_usd * quantity
    print("Above ${:.2f} warning triggered!".format(warn_at_usd))
    quantity_confirm = input("You're about to trade ${:.2f}!\nConfirm the quantity in BTC > ".format(usd))
    if quantity_confirm != args.quantity:
        abort("Numbers don't match.")

if action != 'buy' and action != 'sell':
    abort('Action must be buy or sell')

print("EXCHANGE {}".format(exchange))

price_pump = 0.00000001
if not fast or rate is None or rate.find('%') > -1 or re.search('[a-z]', rate):
    priceMap = p.returnTicker()

    if exchange not in priceMap:
        abort("Currency {} not found".format(exchange))

    # to buy go under the lowestAsk
    # to sell go over highest bid
    #
    # highest bid < lowest ask
    #  ^ sell         ^ buy
    #
    row = priceMap[exchange]

    ask = float(row['lowestAsk'])
    bid = float(row['highestBid'])
    last = float(row['last'])
    perc = 0

    spread = 1 - bid / ask

    rateStr = rate
    if rate:
        word, oper, amount = re.search('([a-z]*|)([+-]|)([0-9\.]*%|[\d\.]*|)', rate).groups()
    else:
        word, oper, amount = '', '', ''
    rate = None

    if word == 'ask':
        rate = ask

    if word == 'bid':
        rate = bid

    if word == 'last':
        rate = last

    if word in ['break', 'profit', 'lowest', 'highest']:
        hist = lib.analyze(lib.tradeHistory(exchange), currency=exchange)

        if word == 'lowest':
            if action == 'buy':
                rate = hist['lowestBuy']

            if action == 'sell':
                warn("You are trying to sell at your lowest selling point")
                rate = hist['lowestSell']

        elif word == 'highest':
            if action == 'buy':
                warn("You are trying to buy at your highest buying point")
                rate = hist['highestBuy']

            if action == 'sell':
                rate = hist['highestSell']

        elif word == 'break':
            rate = hist['break']
            if rate < 0:
                abort("Break point is under 0: {}".format(rate))
        elif word == 'profit':
            rate = max(hist['buyAvg'], hist['break']) + price_pump

    # We're here if we didn't do a word
    if rate is None:
        if spread > spreadThreshold:
            compare = False
            if action == 'buy':
                rate = (1 + spread / 10) * bid 
                compare = ask
            else:
                rate = ask * (1 - spreadThreshold)
                compare = bid

            warn("Spread is over threshold:\n {:.8f} Would have done this\n {:.8f} Doing this instead\n {:.8f} Delta".format(compare, rate, abs(compare - rate)))
        else:
            rate = ask if action == 'buy' else bid


    baseRate = rate

    if amount.find('%') > -1:
        perc = float(amount.replace('%', '')) / 100
        if oper == '-':
            rate *= 1 - perc
        elif oper == '+':
            rate *= 1 + perc
        else:
            if perc < 0.5:
                warn("Requesting a rate {:.0f}% below market".format(100 * (1-perc) ))
            rate *= perc

    if args.nofee: 
        rateOrig = rate
        if action == 'buy' and rate == ask:
            rate = rate - price_pump
        elif action == 'sell' and rate == bid:
            rate = rate + price_pump

        if rateOrig != rate:
            lib.bprint(" Trying to avoid fee by adding {:.8f}".format(price_pump))
        else:
            lib.bprint(" Price isn't at the market price. Nothing changed")

    lib.bprint(" Bid:  {:.8f}\n Last: {:.8f}\n Ask:  {:.8f}\n Sprd: {:.8f}".format( bid, last, ask, spread))
    lib.bprint("\n Rate:  {:.8f}\n Perc:  {:.8f}\n Total: {:.8f}".format(baseRate, perc, rate))

# The market is done in 10^-8 btc so we need to round our rate to that to get proper fractional calculations
fl_rate = round(float(rate) * 1e8) / 1e8
lib.bprint("\nComputed\n Rate  {:.8f}\n Quant {:.8f}\n USD   {:.3f} (btc={:.2f})".format(fl_rate, float(quantity), float(quantity) * approx_btc_usd, approx_btc_usd))

if not fast:
    balanceMap = lib.returnCompleteBalances()
    row = balanceMap[currency]

    print("\nBalance:\n BTC   {:>13}\n {:6}{:13.8f}".format(
        row['btcValue'], currency, float(row['onOrders']) + float(row['available'])
      ))

quantity += .499 * satoshi
amount_to_trade = quantity / fl_rate
lib.bprint("\n{}\n   {:12.8f}\n * {:12.8f}BTC\n = {:12.8f}BTC".format(action.upper(), amount_to_trade, fl_rate, quantity))

if quantity == 0:
    sys.exit(-1)

if False or not fast:
    wait = 2
    print("\nWaiting {} seconds for user abort".format(wait))
    for i in range(wait, 0, -1):
        print("...{}".format(i - 1), end='', flush=True)
        try:
            time.sleep(1)
        except: 
            abort("Trade Halted")

    print("")

if action == 'buy':
    if not fast:
        if fl_rate > (lowest * 1.2):
            abort("{:.10f}BTC is the lowest ask.\n{:.10f}BTC is over 20% more than this!".format(lowest, fl_rate))

    if args.nofee:
        buy_order = p.buy(exchange, rate, amount_to_trade, orderType='postOnly')
    else:
        buy_order = p.buy(exchange, rate, amount_to_trade)

    lib.showTrade(buy_order, exchange, trade_type='buy', rate=rate, amount=amount_to_trade)

elif action == 'sell':
    if not fast:
        if fl_rate < (bid * 0.8):
            abort("{:.10f}BTC is the highest bid.\n{:.10f}BTC is over 20% less than this!".format(lowest, fl_rate))
    
    sell_order = p.sell(exchange, rate, amount_to_trade)
    lib.showTrade(sell_order, exchange, trade_type='sell', rate=rate, amount=amount_to_trade)

