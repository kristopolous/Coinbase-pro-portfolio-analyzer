#!/usr/bin/python3
from poloniex import Poloniex
import json
import sys
import time
import secret
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--currency", required=True, help="Currency to buy")
parser.add_argument('-a', "--action", required=True, help="Action, either buy or sell")
parser.add_argument('-q', "--quantity", default=0, help="Quantity to buy, expressed as in btc")
parser.add_argument('-r', "--rate", default=None, help="Rate (defaults to market). Also accepts last, low and percent")
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
approx_btc_usd = 4500

# let's set it really low for now. 
warn_at_usd = 3.50

def abort(msg):
    print("\nERROR:\n {}\n\n Aborted.".format(msg.replace('\n', '\n ')))
    sys.exit(-1)

def show_trade(order):
    print("\nSUCCESS:")

    for trade in order['resultingTrades']:
        print(" {}\n {}{} at {}BTC.\n Total {}BTC\n\n".format(trade['type'], trade['amount'], currency, trade['rate'], trade['total']))

    with open('order-history.json','a') as f:
        f.write("{}\n".format(json.dumps(order)))

if quantity > (warn_at_usd / approx_btc_usd):
    usd = approx_btc_usd * quantity
    print("Above ${:.2f} warning triggered!".format(warn_at_usd))
    quantity_confirm = input("You're about to trade ${:.2f}!\nConfirm the quantity in BTC > ".format(usd))
    if quantity_confirm != args.quantity:
        abort("Numbers don't match.")

if action != 'buy' and action != 'sell':
    abort('Action must be buy or sell')

print("EXCHANGE {}".format(exchange))

if not fast or rate is None or rate.find('%') > -1 or rate == 'last':
    priceMap = p.returnTicker()

    if exchange not in priceMap:
        abort("Currency {} not found".format(exchange))

    row = priceMap[exchange]
    lowest = float(row['lowestAsk'])
    bid = float(row['highestBid'])

    print(" Bid:  {}\n Last: {}\n Ask:  {}\n Spread: {}".format(row['highestBid'], row['last'], row['lowestAsk'], 1 - float(row['highestBid']) / float(row['lowestAsk'])))

    last = row['last']
    if rate is None:
        rate = row['lowestAsk'] if action == 'buy' else row['highestBid']
        if args.nofee and action == 'buy':
            price_pump = 0.00000001
            print(" Trying to avoid fee by adding {:.8f}".format(price_pump))
            rate = float(rate) - price_pump

    elif rate == 'last':
        rate = last
    elif rate == 'low' or rate == 'lowest':
        rate = bid
    elif rate.find('%') > -1:
        perc = float(rate.replace('%', '')) / 100
        rate = perc * float(last)

fl_rate = float(rate)
print("\nComputed\n Rate  {:.10f}BTC\n Quant {:.10f}BTC\n USD  ${:.2f}".format(fl_rate, float(quantity), float(quantity) * approx_btc_usd))

if not fast:
    balanceMap = p.returnCompleteBalances()
    row = balanceMap[currency]

    print("\nBalance:\n BTC   {:>13}\n {:6}{:13.8f}".format(
        row['btcValue'], currency, float(row['onOrders']) + float(row['available'])
      ))

amount_to_trade = quantity / fl_rate
print("\n{}\n {:.8f}{} at {:.8f}BTC.\n Total {:.8f}BTC".format(action.upper(), amount_to_trade, currency, fl_rate, quantity))

if quantity == 0:
    sys.exit(-1)

if False or not fast:
    wait = 8
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

    show_trade(buy_order)

elif action == 'sell':
    if not fast:
        if fl_rate < (bid * 0.8):
            abort("{:.10f}BTC is the highest bid.\n{:.10f}BTC is over 20% less than this!".format(lowest, fl_rate))
    
    sell_order = p.sell(exchange, rate, amount_to_trade)
    show_trade(sell_order)

