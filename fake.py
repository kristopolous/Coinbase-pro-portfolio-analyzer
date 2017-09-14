def trade(what, tradeList, amount, price):
    tradeList.append({
      'rate': price,
      'amount': amount,
      'total': price * amount,
      'type': what
    })

def sell(tradeList, amount, price):
    trade('sell', tradeList, amount, price)

def buy(tradeList, amount, price):
    trade('buy', tradeList, amount, price)
