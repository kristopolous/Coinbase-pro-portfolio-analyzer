# Coinbase Pro Portfolio Analyzer

Features:

  * Average Buy / Sell
  * Total Buy / Sell
  * Breakeven points
  * P/L per-currency
  * Snapshot peformance graphs
  * Optional combination of USD and USDC markets on a per-currency basis
  * ROI slice by investment amount, liquidation date, or historic date
  * Includes assessments of currency amounts that exited coinbase
  * DOES NOT execute trades or otherwise modify any positions or holdings
  * Written in Python3 and runs on the command line

![graph](https://raw.githubusercontent.com/kristopolous/Coinbase-pro-portfolio-analyzer/master/pn.png)

## Summary view
Let's start with the average buy/sell, current holdings, and how the current traded price fairs
with respect to your averages for a given exchange.

```
$ cbport -s
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
```

The right hand side of the exchange we'll be calling USD here but it works
for any exchange (such as BTC-ETH for instance). It's a shorthand for the 
presumed largest use-case which is buying and selling with USD.

The left-hand side we'll refer to as COIN just as a shorthand to refer to any
instrument (usually a crypto coin) in the LHS of an exchange. 

The PRICE (in caps) is the last trade price as returned by coinbase (there's a 1 hour redis
cache on the value that can be purged with --update)

For example, if you're buying Bitcoin with dollars, the exchange would be BTC-USD and
Bitcoin is COIN and dollars here is USD. The parenthetical at the end will refer to
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
 * M - COMPUTED total COIN you have (this should account for aggregate transfers both ways)
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

Additionally:
 
 * The overall profit of all my trades so far is +29% (bought things at $16.12, sold them at $20.75).
 * My breakeven point to make that extra $0.25 back from the current $97.68 is currently impossible since my position is at 0.

So if my investment goal was simply "make back principle" then I can claim success on this position.

## Filtering
You can look at your investments by USD amount bought/sold (`-a`), since liquidation (`-z`), or number of days (`-d`). You can also filter 
exchanges by regular expression (such as say, to only look at LTC or USDC).

### Amount
For instance if I wanted to look at only the last $80 or so I invested in Litecoin I can do this:

```
$ cbport -sq LTC -a 80
LTC-USD    buy:    219.19    75.00    0.3422 -10       0.025 (4.94)
  196.43   sell:   173.27    78.74    0.4545 +13      -0.112 (-22.06)
     ...    ...       -21     3.74      8.68 +1

TOTAL: 
 bought:      75.03
   sold:      78.74
    p/l:       3.71
```
Here I can see that the last $80 I bought LTC with I averaged at $219.19 and the last $80 I sold I averaged at $173.27. This
of course means that I sold more than I bought for those $80, not great.

This could tell me for instance, that maybe for my next $80 I'd like to buy averaging below 219 and sell averaging above whatever
that becomes.

### Days
Let's look at Litecoin again but now over the past 10 days.

```
$ cbport -usq LTC -d 10
LTC-USD    buy:    197.74    10.00    0.0506 0         0.076 (14.93)
  197.13   sell:   160.73   130.12    0.8096 +23      -0.759 (-149.62)
     ...    ...       -19   120.12    135.05 +1

TOTAL:
 bought:      10.00
   sold:     130.12
    p/l:     120.12
```

After the first assessment I decided to buy $10 at the market rate. I ran with the `-u` option to pull down my latest trades
and reflect that.

### Zero
Let's look at MakerCoin for the last one. Coinbase had a reward system where they gave a small amount of makercoin out. That
was my starting balance. You can see that in the `N` slot (bottom right of the summary) below:

```
MKR-USD    buy:   2862.84   129.98    0.0454 +30       0.003 (9.80)
 3734.57   sell:  2992.85   142.51    0.0476 +25      -0.002 (-8.28)
     ...    ...        +5    12.54     22.34 0

TOTAL:
 bought:     129.98
   sold:     142.51
    p/l:      12.54
```

Here I can see that I sold for 5% more than I bought for. Alright I mean it's up 25% probably should have held that
$129 worth and I would have had $38 in profits instead of $12 but oh well, que sera sera.


## Step analysis
The `--step` and `--end` break up your investments per exchange to see
how in aggregate you are doing. Let's take BCH:


```
$ cbport -q BCH -c --step 10 --end 200
...
  10 buy:    959.87    20.00 10.5387
     sell:  1061.03    30.03

  20 buy:   1082.72    30.00 -2.0035
     sell:  1061.03    30.03

  A  buy:   B          C     D
     sell:  E          F    

  30 buy:   1049.44    40.00 1.1039
     sell:  1061.03    30.03

  40 buy:   1029.84    50.00 2.2380
     sell:  1052.88    59.60

```

Sometimes the interest isn't so much as in whether this is still a profitable decision overall in as much as whether it's a profitable decision for the last say, $100 bought.  So this allows a consideration for ONLY recent money.

 * A - In the last $A bought and $A sold, or as close as we can come, how 
did the P/L perform.
 * B - Average buy prices over A
 * C - Bought amount we're considering (trying to approximate A)
 * D - P/L % (as in I was up 10%, down 2, up 1, up 2 etc)
 * E - Average sell
 * F - The total amount sold used for the calculation


## Unicode graph (-g)
The `-g` option will give you these nifty little lines in front.

What you're seeing is a percentage change in the past 24 hours. They are all normalized as in the exchange with the most change
has the largest delta. The first column is open, second is low, third is last. The top is always the high (the ANSI underline of the line
above forms the ceiling in this case)

So that means that in this example both MKR and MIR are up. On a percentage points basis, MKR is up more than MIR (you can see that
in the `T` labeled field as well). Here MKR is a currency I hold 0 of and it's now +7% of my average sale which means I lost money
by selling it too early. For MIR, it's somewhat the opposite. I've put $19.82 in and it's at $8.07 right now. If I liquidated now I
will be down $11.75 so I might as well either hold or buy more or if I have given up all hope just take my $8 back ... decisions decisions...

```
$ cbport -cgsd 300
```
![graph](https://raw.githubusercontent.com/kristopolous/Coinbase-pro-portfolio-analyzer/master/res.png)

# Installation

 1. You'll need `redis` for the cache 
 2. Create a `secrets.py` file. 
    * Look in the `coinbase` directory
    * Copy `secrets.py.example` to `secrets.py`.
    * Go to [https://www.coinbase.com/settings/api](https://www.coinbase.com/settings/api) to create an API key.
    * Insert the values into your `secrets.py` file.

## Notes

 * Prices are on a 1 hour cache
 * Trade history is cached but not updated unless you explicitly ask "-u" or "--update".
 * Settled trades (historicals) are stored without any cache updating rules.

### Usage

Use `cbport --help`

