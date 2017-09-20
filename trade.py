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
parser.add_argument('-q', "--quantity", default=0, help="Quantity to buy, expressed as in btc")
parser.add_argument('-r', "--rate", default=None, help="Rate (defaults to market). Also accepts last, high, low and percent")
parser.add_argument('-n', "--nofee", action='store_true', help="Try to avoid the higher fee")
parser.add_argument('-f', "--fast", action='store_true', help="Skip the ceremony and do things quickly")
args = parser.parse_args()

p = Poloniex(*secret.token)

currency = args.currency.upper()
exchange = 'BTC_{}'.format(currency)
quantity = float(args.quantity)
rate = args.rate
action = args.action.lower()
fast = args.fast
lowest = False

# This is only used for the warning message to make sure
# the fingers don't slip and someone buys/sells the farm
# (say by leaving out a decimal point)
#
# curl https://api.coindesk.com/v1/bpi/currentprice.json
#
approx_btc_usd = lib.btc_price()

# let's set it really low for now. 
warn_at_usd = 3.50

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

if not fast or rate is None or rate.find('%') > -1 or re.search('[a-z]', rate):
    priceMap = p.returnTicker()

    if exchange not in priceMap:
        abort("Currency {} not found".format(exchange))

    row = priceMap[exchange]
    lowest = float(row['lowestAsk'])
    ask = bid = float(row['highestBid'])

    if rate == 'ask':
        rate = 'high'

    spread = 1 - float(row['highestBid']) / float(row['lowestAsk'])

    last = row['last']
    if rate is None:
        if spread > 0.005:
            rate = (1 + spread / 10) * bid if action == 'buy' else row['highestBid']
        else:
            rate = row['lowestAsk'] if action == 'buy' else row['highestBid']

    elif rate == 'last':
        rate = last
    elif rate == 'high' or rate == 'highes':
        rate = lowest
        # we don't need to price pump at the ask price
        args.nofee = False
    elif rate == 'low' or rate == 'lowest':
        rate = bid
    elif rate.find('%') > -1:
        perc = float(rate.replace('%', '')) / 100
        rate = perc * float(last)

    if args.nofee: 
        price_pump = 0.00000001
        print(" Trying to avoid fee by adding {:.8f}".format(price_pump))
        if action == 'buy':
            rate = float(rate) - price_pump
        else:
            rate = float(rate) + price_pump

    marker = '   '
    if rate == 'low':
        marker = '>  '
    if rate == 'last':
        marker = ' > '
    if rate == 'high':
        marker = '  >'
    lib.bprint("{}Bid:  {}\n{}Last: {}\n{}Ask:  {}\n Sprd: {:.6}".format(marker[0], row['highestBid'], marker[1], row['last'], marker[2], row['lowestAsk'], spread))

fl_rate = float(rate)
lib.bprint("\nComputed\n Rate  {:.8f}\n Quant {:.8f}\n USD   {:.3f} (btc={:.2f})".format(fl_rate, float(quantity), float(quantity) * approx_btc_usd, approx_btc_usd))

if not fast:
    balanceMap = lib.returnCompleteBalances()
    row = balanceMap[currency]

    print("\nBalance:\n BTC   {:>13}\n {:6}{:13.8f}".format(
        row['btcValue'], currency, float(row['onOrders']) + float(row['available'])
      ))

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

