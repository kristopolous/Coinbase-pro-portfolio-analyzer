# Coinbase Pro Portfolio Analyzer

Coinbase doesn't really give great tools that allow you to make profit/loss judgements. 

This tool seeks to do that without being too fancy. Let me show you an example:


If I run the tool as such

```
$ ./cbport --average
```

I'll get output like this (last one is a key)

```
...
 NU-USD    buy:      0.51    91.52  181.1291 -21      92.282 (36.98)
    0.40   sell:     0.69    71.79  103.3419 -42      77.787 (31.17)
    0.21    +87       +37   -19.73     17.24 +4

 OGN-USD   buy:      2.39    49.93   20.8500 -52      20.850 (23.91)
    1.15   sell:     0.00     0.00    0.0000 ...      20.850 (23.91)
    2.39    -52       ...   -49.93    -26.02 -4

 A         buy:       B         C        D    E          F   ( G   )
    H      sell:      I         J        K    L          M   ( N   )
    O        P        Q         R        S    T
...
```

Let me go over what this is, and yes I know this looks like a lot, but it's
really not.  These all can be scoped by a "region of interest" such as an
amount of time, money, or starting from when your balance for a particular 
currency was last at 0 (as in liquidated/empty).

**Notes:** 

The right hand side of the exchange we'll be calling dollars here but it works
for any exchange (such as BTC-ETH for instance). It's a shorthand for the 
presumed largest use-case which is buying and selling with USD.

The left-hand side we'll refer to as COIN just as a shorthand to refer to any
instrument (usually a crypto coin) in the LHS of an exchange. 

The PRICE (in caps) is the last trade price as returned by coinbase (there's a 1 hour redis
cache on the value that can be purged with --update)

For example, if you're buying bitcoins with dollars, the exchange would be BTC-USD and
bitcoins is COIN and dollars USD. The parenthetical at the end will refer to
trader lingo, if it helps.

### Row 1: buy-centric

 * A - Exchange we're looking at
 * B - Average USD you've bought COIN at
 * C - Total USD you've spent (Total cost)
 * D - Total COIN you've bought (Total position quantity)
 * E - Percentage difference of the PRICE from your average buy (P/L %)
 * F - How much COIN you currently have as reported by coinbase. (Current position quantity)
 * G - How much USD this is.

### Row 2: sell-centric

 * H - Last price
 * I - Average USD you've sold COIN at
 * J - Total USD you've sold COIN
 * K - Total COIN you've sold
 * L - Percentage difference of the PRICE from your average sell
 * M - COMPUTED total COIN you have (this should account for transfer outs but not transfer ins)
 * N - How much USD this is.

### Row 3: action-centric

 * O - The break-even price needed to sell your existing position in COIN and make your principle USD back.
 * P - How far, as a percent, the current price is from your break-even.
 * Q - The percentage difference between your average sell and average buy (or `...` if you haven't sold)
 * R - How much of your principle USD is still in the market 
 * S - What your total USD return would be if you sold all your COIN at the current price (profit/liquidation return)
 * T - The change in the past 24 hours
 
For instance:

#### NU-USD 

 * I still have $19.73 USD "in the market" accounting for all my buys and sells.
 * If I liquidated my $36.92 position this would yield $17.24 more than I started (profit).

#### OGN-USD

 * I still have all my $49.93 USD "in the market" and have sold nothing.
 * If I liquidated my position I'd walk away losing $26.02 (loss)

A note about (M), I had transferred 92.282 - 77.787 (14.544) NU in from somewhere else. This calculation
can remind you either that you have transferred out some COIN quantity you bought in coinbasepro or that 
you've brought in some COIN quantity from somewhere else (another exchange/private wallet/reward, etc).

It also allows you to do computation say if you bought LTC on coinbase and then put it over to say, regular
Coinbase, Celsius or Blockfi. For instance, Coinbase offers a staking reward for ATOM so I'll see this:

```
 ATOM-USD  buy:     16.12   303.21   18.8050 +44       0.000 (0.00)
   23.23   sell:    20.75   302.95   14.6000 +12       4.205 (97.68)
    0.00    ...       +29    -0.25       ... +3
```

I can see here that I

 1. Bought $303.21 worth of ATOM averaging $16.12. 
 2. Sold $302.95 averaging $20.75.
 3. Am down only $0.25 from my principle (the amount of money I put in). Effectively I got all my money back minus 25 cents.
 4. Transferred the remaining ATOM (about $97.68 worth) to somewhere else (in this case on regular coinbase for the staking reward).

## Unicode graph (-g)
The `-g` option will give you these nifty little lines in front.

What you're seeing is a percentage change in the past 24 hours. They are all normalized as in the exchange with the most change
has the largest delta. The first column is open, second is low, third is last. The top is always the high.

So that means that in this example both SUSHI and TRB are up. On a percentage points basis, SUSHI is up more than TRB (you can see that
in the `T` labeled field as well)
![graph](https://raw.githubusercontent.com/kristopolous/Coinbase-pro-portfolio-analyzer/master/res.png)

Additionally:
 
 * The overall profit of all my trades so far is +29% (bought things at $16.12, sold them at $20.75).
 * My breakeven point to make that extra $0.25 back from the current $97.68 is currently impossible since my position is at 0.

So if my investment goal was simply "make back principle" then I can claim success on this position.

## Installation

 1. You'll need `redis` for the cache 
 2. Create a `secrets.py` file. 
    * Look in the `coinbase` directory
    * Copy `secrets.py.example` to `secrets.py`.
    * Go to [https://www.coinbase.com/settings/api](https://www.coinbase.com/settings/api) to create an API key.
    * Insert the values into your `secrets.py` file.

### Usage

Use `./cbport --help`

