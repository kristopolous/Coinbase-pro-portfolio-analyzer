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
parser.add_argument('-r', "--rate", default=None, help="Rate (defaults to market). Also accepts last and percent")
parser.add_argument('-f', "--fast", action='store_true', help="Skip the ceremony and do things quickly")
args = parser.parse_args()

p = Poloniex(*secret.token)

currency = args.currency.upper()
exchange = 'BTC_{}'.format(currency)
quantity = float(args.quantity)
rate = args.rate
action = args.action
fast = args.fast
lowest = False

def abort(msg):
    print("\nERROR:\n {}\n\n Aborted.".format(msg.replace('\n', '\n ')))
    sys.exit(-1)

def show_trade(order):
    print("\nSUCCESS:")

    for trade in order['resultingTrades']:
        print(" {}{} at {}BTC.\n Total {}BTC\n\n".format(trade['amount'], currency, trade['rate'], trade['total']))

    with open('order-history.json','a') as f:
        f.write("{}\n".format(json.dumps(order)))

if quantity > 0.001:
    usd = 4600 * quantity
    quantity_confirm = input("You're about to trade ${:.2f}!\nConfirm this and enter that again > ".format(usd))
    if quantity_confirm != args.quantity:
        abort("Numbers don't match. no trade")

print("EXCHANGE {}".format(exchange))

if not fast or rate is None or rate.find('%') > -1 or rate == 'last':
    priceMap = p.returnTicker()

    if exchange not in priceMap:
        abort("Currency {} not found".format(exchange))

    row = priceMap[exchange]
    lowest = float(row['lowestAsk'])

    print(" Bid:  {}\n Last: {}\n Ask:  {}".format(row['highestBid'], row['last'], row['lowestAsk']))

    last = row['last']
    if rate is None:
        rate = row['lowestAsk'] if action == 'buy' else row['highestBid']
    elif rate == 'last':
        rate = last
    elif rate.find('%') > -1:
        perc = float(rate.replace('%', '')) / 100
        rate = perc * float(last)

fl_rate = float(rate)
print("\nComputed\n Rate  {:.10f}BTC\n Quant {:.10f}BTC".format(fl_rate, float(quantity)))

if not fast:
    balanceMap = p.returnCompleteBalances()
    row = balanceMap[currency]

    print("\nBalance:\n BTC   {:>13}\n {:6}{:13.8f}".format(
        row['btcValue'], currency, float(row['onOrders']) + float(row['available'])
      ))

amount_to_buy = quantity / fl_rate
print("\n{}\n {}{} at {:.10f}BTC.\n Total {:.10f}BTC".format(action.upper(), amount_to_buy, currency, fl_rate, quantity))

if quantity == 0:
    sys.exit(-1)

"""
if False or not fast:
    wait = 8
    print("\nWaiting {} seconds for user abort".format(wait))
    for i in range(wait, 0, -1):
        print("...{}".format(i - 1), end='', flush=True)
        time.sleep(1)
"""

if action == 'buy':
    if not fast:
        if fl_rate > (lowest * 1.2):
            abort("{:.10f}BTC is the lowest ask.\n{:.10f}BTC is over 20% more than this!".format(lowest, fl_rate))

    buy_order = p.buy(exchange, rate, amount_to_buy)
    show_trade(buy_order)

elif action == 'sell':
    if args.quantity == 0:
        print("I'd be selling {} at {}. But not right now.".format(currency, rate))
        sys.exit(-1)

else:
    print("action has to be either buy or sell")
