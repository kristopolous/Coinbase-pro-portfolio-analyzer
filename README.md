Some cryptocurrency market analysis tools

The goal of my current pursuit is to determine whether buying or selling is a good idea given my portfolio

Nothing personal is here and you'll have to modify secrets.py.example in order for it to work for you.

### practice and theory

I've been trading bitcoins since 2010 but never in serious enough amounts to be rich.

For me it's more about learning about markets and how human think collectively.

Anyway, there's two things here ... one of them does something called Dollar-Cost-Averaging (DCA), which is
usually a bad strategy when used naively or blindly, and the other is tranche profits + DCA. 

Ultimately you want to sell more than you buy and so total sell / total buy > 1.0.  Pretty easy right?

The problem is that when the price goes down, and I mean substantially, you can't just wait and hope for
it to return to some prior high ... it may never get there.

You could reduce your DCA by buying more at the lower price, but in practice, you may end up throwing lots of
money at the losers in your portfolio and not focusing on the near-winners.  It's a high-risk, low-return,
high-investment strategy.  Bad idea.

But what else do you do other than write-off a dropped investment?

Here come tranches.  If you *ignore* the higher prices you paid, for now.  Now you just try to make a profit
at the new (lower) normal off of its volitility.  If you do a few rounds (buy/sell) then you lower your DCA
cost because that's total cost, you lower your total invested, because you sold, and you lower your break-even
point becaues you've profited.  

So you can tranche your holdings of some asset into different pricing tiers based on your holdings and then you
consider the prospect of buying or selling based on each tier + variability in the market place.

This is the current work in progress and it's mathematically sound and likely to work.  (see running.py and tranche.py)

I'm pretty sure this is a known strategy and there's wikipedia page with lots of solid math on it, but then
it wouldn't be as much fun.

Besides, all of these tools here essentially trade in 0.0001 btc at a time (which is as of this writing, about
$.35).  Again, I was never in it to make money (although I've made a bit).

> The big hypothesis here is since the fees are small, to try to make small profits from large holdings in short times and then re-invest.

As an investor in traditional stocks, I've been screwed one too many times using the preferential lump-sum investment strategy where the companies I invested in end up dissappearing in 10 years or get bought or merged and I'm out of investment. I've come to appreciate the idea that a long-term hold in some 40% gain expectation is almost more risk than an expectation of 3-5% return in a matter of days or weeks. It also locks your liquid funds away in something you are just waiting for a sunny day on. Yeah, fuck that.

#### disclaimer

If you're looking for a set-it-and-forget-it make-money-while-i-sleep magic trading bot, then I've got two 
pieces of news for you:

 * Most strategies are only effective when they are secret
 * You're unlikely to outsmart the other bots

There's institutional investors in crypto trading now -- this means MIT and Harvard math PHDs, $400/hr world class
programmers and people making custom hardware. It's admirable to think you can out-fox them, but you likely won't.

So you probably can't find this and you are unlikely to be able to make it ... or who knows, maybe all those people
are dumb... it's happened before.

### history.py

A cli histogram for your buys for a currency.  Let's see how foolish I've been with namecoin:

```
$ ./history.py nmc
_.___3253>
_.___3331
_.___3410
_.___3489
_.___3567^
_.___3646 *******
_.___3725
_.___3803 ***
_.___3882 ******
_.___3961
_.___4039 ******
_.___4118 ***
_.___4197
_.___4275 **********
_.___4354 ***************
_.___4432 *********************
_.___4511 **********************
_.___4590
_.___4668
_.___4747 *******************************
_.___4826 **********************
```

Key:
 * `>` - where the last trade happened. 
 * `*` - my distributions of that inclusive range.  
 * `^` - the lowest buy I've made up to this point. 
 * `_` - Replacements for 0s to make things easier to see at a glance

So we can see that namecoin is trading at 0.0003253 and my lowest buy is at 0.0003652. Oops! Trading can be difficult!

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

Waiting 2 seconds for user abort
1...0
SUCCESS:
 buy
 6.88774104RIC at 0.00001452BTC.
 Total 0.00010000BTC

</pre>


### open.py

Shows the open orders on a given currency or all.  

For instance, here are my hopes and dreams for Ripple (stars have been added to this example to provide a futile cloak of anonymity):

```
$ ./open.py xrp
BTC_XRP
 buy  0.00084000
  7517406**** 2017-08-30 02:42:** 0.00004200 0.00084000
 sell 0.00050000
  7876304**** 2017-09-15 07:32:** 0.00005500 0.00010000
  7876665**** 2017-09-15 07:50:** 0.00005550 0.00010000
  7876308**** 2017-09-15 07:33:** 0.00005600 0.00010000
  7876668**** 2017-09-15 07:50:** 0.00006500 0.00010000
  7876673**** 2017-09-15 07:51:** 0.00007000 0.00010000
```

So if the price gets to 0.00005600, I'm going to sell a whole 0.0001 btc of it. 
That's Big money now - like parking-meter change. Those are UTC times there.

### monitor.py

Part reality, part snake oil, this tool shows an overview of your current holdings and is updated in a polite-to-poloniex approximation
of real-time (every 10 seconds as of this writing):

It runs full screen and does an update. There's a lot to be wanted but it's not bad right now. Here's an example with  --- 8< ---
signifying truncation of output. Things have also been numbered for the description below

```
  cur     avgbuy    price     roi       bal      prof       buy      sell     delta
  XPM    0.09638  0.03831  39.748    44.303   -26.693   47.6239  -47.9263   96.8847
  SC     0.00243  0.00131  53.862    60.357   -27.848   28.4528  -28.6441   96.7046
  --- 8< ---
  REP    5.25056  4.91170  93.546    95.799    -6.183    3.8704   -3.9161   94.2984
  XRP    0.05311  0.05015  94.420    38.945    -2.173    2.0197   -2.0342   96.4731
  --------------------------------------------------------------------------------- (profit line)
  OMG    2.67470  2.73046 102.085     2.390     0.050  -24.8359   31.7263   29.3971
  ETH   60.68039 69.85933 115.127   128.092    19.376   -1.4543    1.4575   98.9159
  --- 8< ---
  -235.09363 -235.26934 -237.22884  (running balance)
  -235.15078 -236.92644 -237.39766
  -235.57001 -235.96676 -237.31935
  -234.47959 -237.30898
  --- 8< ---
```

The tool lists all of your `BTC_*` market holdings along with the following real columns:

  * avgbuy - What your average buy is in 1/1000 btc
  * price - The last traded price in 1/1000 btc
  * roi - Return on investment of current holdings, in percent, essentially the price / avgbuy
  * bal - Estimated USD of holdings based on a twice daily update of btc price from coindesk
  * prof - Estimated USD profit if you were able to sell off all holdings at `price`

And the following snake-oil columns:
  * buy - How a 0.0001btc buy of the currency would change your avgbuy number. If this number is big then your average buy will go down if you buy the currency ... this means that profit may be closer in reach.
  * sell - How a 0.0001btc sell of the currency would change your avgsell number on your remaining holdings. This is not considering any profit and is likely complete nonsense.
  * delta - the fractional difference between the two expressed as a triple squareroot. Since the sell number is likely a bad computation, this is also probably a bad thing.


Other properties:

  * the "profit line" is where outright profit can be made without any hedging. This is currently a deceiving line if you have fully invested and divested in a currency at multiple points. It ignores what's called "prior exits" which is if you sold off all of your holdings at a profit at a prior date. This attempts to treat your current holdings as an isolated set.

  * the "running balance" is estimated USD ROI of your current holdings.  How I trade this runs negative because as the strategy in the intro was discussing, the point is to sell off at profit and invest at loss.
