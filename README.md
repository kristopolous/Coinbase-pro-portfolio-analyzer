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
$.45).  Again, I was never in it to make money (although I've made a bit).

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
