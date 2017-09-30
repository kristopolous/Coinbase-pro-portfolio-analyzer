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

In most of the tools, leading 0s are replaced with _ to make things easier to read. You'll get used to it real fast.

### history.py

A cli histogram for your buys for a currency.  I've gotten a bit lucky with Bitcoin Plus here.

 * magenta bars are the buy points
 * green area is the sell points. 
 * number with the blue background is where the last trade happened.

<img src=https://i.imgur.com/tSNqfyF.png>

### trade.py

This is a cli trader for poloniex, whose website is a little lame at times.

Here's an example of it in action, buying a very small amount. 
There's a few features and overrides to avoid from doing something stupid.

The rate is pretty expressive and can have computations:

  * lowest - the lowest price you either bought or sold
  * highest - the highest price you either bought or sold
  * last - the last price a trade was made
  * bid - the current bid price
  * ask - the current ask price
  * break - your breakpoint price for profit
  * profit - either you average buy, or your breakpoint price, whichever is greater

The computations can be done in percentages based on these.  So you can do something like

    -r profit+3% -a sell

Which means you want to open a sale at your profit price + 3%.

    -r lowest-5% -a buy

This means you want an order that is 5% less than your lowest buying point 

    -r 105% -a sell
    -r +5% -a sell
    -r 95% -a buy
    -r -5% -a buy

In the first two, this will sell at the current bid price + 5% and in the second two you'll buy at the current ask price - 5%.

#### Example

I'm going to sell ARDR at the market minimum quantity at my profit point + 1%.
<pre>
$ ./trade.py -fq min -c ardr -r profit+1% -a sell                                                                                                                            
EXCHANGE BTC_ARDR
 Bid:   .____4290
 Last:  .____4290
 Ask:   .____4331
 Sprd:  .__946664

 Rate:   .____4661
 Perc:   ._1000000
 Total:  .____4708

Computed
 Rate   .____4708
 Quant  .___10001
 USD    .418 (btc=4179.32)

SELL
     2.12421941
 *    .____4708BTC
 =    .___10001BTC
15195158808 BTC_ARDR  Open sell  .____4708 * 2.12421941 = .___10001btc
</pre>

At the end I get:

  * The order number which can be canceled with `cancel.py`.
  * A record of the transaction appended to `order-history.json`


### open.py

Shows the open orders on a given currency or all.  

For instance, here are my hopes and dreams for Ripple:

<img src=https://i.imgur.com/yxGeGXp.png>

There's some color codes here:

  * red (orangish with my pallete) - you are selling at a loss (below average buy)!
  * magenta - you are technically at a profit but below your break-even point
  * no color - you're above break even and above average buy, this is profit.
  * green - you're at profit and above your sell average. If these execute, these are *margin increasing* sells.

### monitor.py

Part reality, part snake oil, this tool shows an overview of your current holdings and is updated in a polite-to-poloniex approximation
of real-time (every 10 seconds as of this writing):

It runs full screen and does an update. There's a lot to be wanted but it's not bad right now. Here's an example with  --- 8< ---
signifying truncation of output.

```
 71 price:2017-09-20 02:56:25 | portfolio:2017-09-20 02:42:26  (update)
cur         buy    move     24h    price      last     roi      bal     prof      sell        to
XPM       50.18    .759   -7.44   ._3556   ._3549*  -61.93   49.431  -30.611  -50.4974   96.9402
SC        33.30   1.681   -4.80   .__119   .__118*  -50.39   59.823  -30.143  -33.5249   96.7475
  --- 8< ---
XRP        1.94    .297     .26   ._4715   ._4703*   -2.88   45.706   -1.315   -1.9640   93.0478
------------------------------------------------------------------------------------------------ (profit line)
ETH      -30.69    .213     .14 72.34125 72.86233     3.23  139.138    4.501   37.5111   36.6607
AMP      -17.27  10.462   30.54   ._4693   ._4651     7.06    9.900     .698   18.1879   77.1303
XMR       -1.00    .256   - .39 24.27688 30.04500    37.11  144.177   53.507    1.0047   99.6321
   22:10    22:46    23:22    23:58    00:34    01:10    01:46    02:22 (running balance)
 -286.02  -291.56  -287.77  -289.74  -288.93  -290.70  -293.65  -295.55
   ._277  - ._399    ._252  - ._783  - .6039  - ._449  - ._137  - .5765
 - .2528    .1263  - ._968    ._585  - .1533  - .6830  - .3239  - .9686
 - .6227    .1688  - .3527  - .1297    ._775  - .5817  - .1898  - .9277
  --- 8< ---
```

Properties:

  * update - a countdown timer along with two timestamps, the first is the last time a ticker was updated, and the second is the last time the portfolio was.
  * profit line - where outright profit can be made without any hedging. This may be a deceiving line if you have fully invested and partially divested in a currency at multiple points. It ignores what's called "prior exits" which is if you sold off *all* of your holdings at a profit at a prior date. This attempts to treat your current holdings as an isolated set.
  * running balance - estimated USD ROI of your current holdings. The subsequent rows of a column are relative percentages for that "period". So you can look across at one row and see how things have been going for the past 4 hours in this case, and then look down to see how your portfolio did relatively.

The columns:

  * buy - How a 0.0001btc buy of the currency would change your avgbuy number. If this number is big then your average buy will go down if you buy the currency ... this means that profit may be closer in reach.
  * move - How the market has moved since the last running balance row
  * 24h - What's happened in percentage, over the past 24 hours
  * price - The last traded price in 1/1000 btc
  * last - The last price *you* traded at. An asterisk means you bought at that price.
  * roi - Return on investment of current holdings, in percent, essentially the price / avgbuy
  * bal - Estimated USD of holdings based on a twice daily update of btc price from coindesk
  * prof - Estimated USD profit if you were able to sell off all holdings at `price`
  * sell - How a 0.0001btc sell of the currency would change your avgsell number on your remaining holdings. This is not considering any profit and is likely complete nonsense.
  * to - the fractional difference between the two expressed as a triple squareroot. Since the sell number is likely a bad computation, this is also probably a bad thing.

