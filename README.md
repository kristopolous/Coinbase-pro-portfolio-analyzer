Some cryptocurrency market analysis tools

The goal of my current pursuit is to determine whether buying or selling is a good idea given my portfolio

Nothing personal is here and you'll have to modify secrets.py.example in order for it to work for you.

### trade.py

This is a cli trader for poloniex, whose website is a little lame at times.

Here's an example of it in action, buying a very small amount of Riecoin.
There's a few features and overrides to avoid from doing something stupid.

<pre>
$ ./trade.py -c RIC -q 0.00010001 -a buy  
EXCHANGE BTC_RIC
 Bid:  0.00001451
 Last: 0.00001452
 Ask:  0.00001452
 Spread: 0.0006887052341597588

Computed
 Rate  0.0000145200BTC
 Quant 0.0001000100BTC
 USD  $0.43

Balance:
 BTC      0.00815788
 RIC    562.22479665

BUY
 6.88774105RIC at 0.00001452BTC.
 Total 0.00010001BTC

Waiting 8 seconds for user abort
...7...6...5...4...3...2...1...0
SUCCESS:
 buy
 6.88774104RIC at 0.00001452BTC.
 Total 0.00010000BTC

</pre>
