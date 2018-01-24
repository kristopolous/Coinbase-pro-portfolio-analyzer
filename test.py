#!/usr/bin/python3 -O
import lib
import btlib
import talib
import numpy as np
import sys
import random

curlist_master = 'BTC_AMP BTC_ARDR BTC_BCH BTC_BCN BTC_BCY BTC_BELA BTC_BLK BTC_BTCD BTC_BTM BTC_BTS BTC_BURST BTC_CLAM BTC_CVC BTC_DASH BTC_DCR BTC_DGB BTC_DOGE BTC_EMC2 BTC_ETC BTC_ETH BTC_EXP BTC_FCT BTC_FLDC BTC_FLO BTC_GAME BTC_GAS BTC_GNO BTC_GNT BTC_GRC BTC_HUC BTC_LBC BTC_LSK BTC_LTC BTC_MAID BTC_NAUT BTC_NAV BTC_NEOS BTC_NMC BTC_NOTE BTC_NXC BTC_NXT BTC_OMG BTC_OMNI BTC_PASC BTC_PINK BTC_POT BTC_PPC BTC_RADS BTC_REP BTC_RIC BTC_SBD BTC_SC BTC_SJCX BTC_STEEM BTC_STORJ BTC_STRAT BTC_STR BTC_SYS BTC_VIA BTC_VRC BTC_VTC BTC_XBC BTC_XCP BTC_XEM BTC_XMR BTC_XPM BTC_XRP BTC_XVC BTC_ZEC BTC_ZRX'.split(' ')

curlist = []
for cur in curlist_master:
    if random.random() < 0.9:
        continue
    curlist.append(cur)

print(" ".join(curlist))

margin = 0.0113
backtrack = 6
#for margin in [  .0115, 0.012, .0125, 0.013, 0.0135, 0.014]: 
#for backtrack in [ 3,6,9,20,80]:
invest = 0.02
for unitfrac in [ 10, 11 ]:
    avg = []
    holdavg = []
    magicavg = []
    tragicavg = []

    for dateSet in [ ['2017-12-01', '2017-12-11'] ]:#, ['2017-10-21', '2017-12-08'], ]:
        count = 0
        ttl = 0
        holdttl = 0
        magicttl = 0
        tragicttl = 0
        for curname in curlist:

            hist = btlib.getHistory(curname, dateSet[0], dateSet[1], 'rate', [' and gid % 20 = 0'])
            if len(hist) == 0:
                continue

            unit = unitfrac/10000.0

            btc = 1.0
            last = hist[0]
            cur = invest / last
            bought = 0
            sold = 0
            btc -= last * cur
            startbtc = btc
            startcur = cur
            below = 1 - margin
            above = 1/below + 0.00005


            for trade in hist:
                if trade > above * last and cur > (10 * unit/trade):
                    sell_unit = unit * 1.008
                    btc += sell_unit
                    cur -= sell_unit / trade
                    sold += sell_unit / trade
                    last = trade

                elif trade < below * last:
                    btc -= unit
                    cur += unit / trade
                    bought += unit / trade
                    last = trade

                else:
                    continue

                # print("{:.8f} {:13.8f} {:.8f} {:.8f} {} {}".format(btc, cur, last, last * cur + btc, bought, sold))

            cur -= 0.0025 * (bought + sold)
            strategy_same = hist[-1] * cur + btc


            """
            The "BEST" strategy will be if we magically know the high
            and low points of the time period and do lump sales and
            buys at those positions
            """
            btc = 1.0
            last = hist[0]
            cur = invest / last
            bought = 0
            sold = 0
            btc -= last * cur

            priceList = list(sorted(hist))
            cur = invest / last
            for x in range(0, int(len(priceList) / 3)):
                rate = hist[-x]
                btc += (cur * rate )
                cur = 0
                sold += cur

                rate = hist[x]
                cur = 0.99 * (invest / rate)
                btc -= invest
                bought += cur
                #print("{:.7f} {:.7f}".format(hist[-x], hist[x]))

            cur -= 0.0025 * (bought + sold)
            strategy_magic = hist[-1] * cur + btc
            print("m {:12.5f} {:12.5f} {:12.5f}".format(hist[-1] * cur, btc, strategy_magic))

            """
            The "WORST" strategy will be the opposite of this.
            """
            btc = 1.0
            last = hist[0]
            cur = invest / last
            bought = 0
            sold = 0
            btc -= last * cur

            rate = min(hist)
            btc += (cur * rate )
            cur = 0
            sold = cur

            rate = max(hist)
            btc -= invest
            cur = invest / rate
            bought = cur

            cur -= 0.0025 * (bought + sold)
            tragic_cur = cur
            tragic_btc = btc
            strategy_tragic = hist[-1] * cur + btc



            btc = 1.0
            last = {'buy': [hist[0]], 'sell': [hist[0]]}
            cur = invest / last['buy'][0]
            bought = 0
            sold = 0
            btc -= last['buy'][0] * cur
            startbtc = btc
            startcur = cur
            below = 1 - margin
            above = 1/below + 0.00005

            for trade in hist:
                lastbuy = max(last['buy'][-backtrack:])
                lastsell = min(last['sell'][-backtrack:])
                if trade > above * lastbuy and cur > (2 * unit/trade):
                    sell_unit = unit * 1.008
                    btc += sell_unit
                    cur -= sell_unit / trade
                    sold += sell_unit / trade
                    last['sell'].append(trade)
                    last['buy'].append(trade)
                    

                elif trade < below * lastsell:
                    btc -= unit
                    cur += unit / trade
                    bought += unit / trade
                    last['buy'].append(trade)
                    last['sell'].append(trade)

                else:
                    continue

                # print("{:.8f} {:13.8f} {:.8f} {:.8f} {} {}".format(btc, cur, last, last * cur + btc, bought, sold))

            cur -= 0.0025 * (bought + sold)
            strategy_frac = hist[-1] * cur + btc
            print("s {:12.5f} {:12.5f} {:12.5f}".format(hist[-1] * cur, btc, strategy_frac))


            #print("{:.8f} {:18.8f} {:.8f} {:.8f} {} {}".format(btc, cur, last, last * cur + btc, bought, sold))

            btc = startbtc
            cur = startcur
            hold = hist[-1] * cur + btc
            print("h {:12.5f} {:12.5f} {:12.5f}".format(hist[-1] * cur, btc, hold))
            print("t {:12.5f} {:12.5f} {:12.5f}".format(hist[-1] * tragic_cur, tragic_btc, strategy_tragic))
            print("")
            ttl += strategy_frac
            holdttl += hold
            magicttl += strategy_magic 
            tragicttl += strategy_tragic
            count += 1.0
            #print("{:10s} {:.8f}".format(curname, strategy - hold))
        avg.append(ttl / count)
        holdavg.append(holdttl / count)
        magicavg.append(magicttl / count)
        tragicavg.append(magicttl / count)

    print("")
    avgstr = [ "{:.8f}".format(x) for x in avg ]
    print("Avg: {:5.1f} {}".format(unitfrac, " ".join(avgstr)))
    avgstr = [ "{:.8f}".format(x) for x in holdavg ]
    print("Avg: {:5.1f} {}".format(unitfrac, " ".join(avgstr)))
    avgstr = [ "{:.8f}".format(x) for x in magicavg ]
    print("Avg: {:5.1f} {}".format(unitfrac, " ".join(avgstr)))
    avgstr = [ "{:.8f}".format(x) for x in tragicavg ]
    print("Avg: {:5.1f} {}".format(unitfrac, " ".join(avgstr)))
#print("{:.8f}".format(0.0015 * (bought + sold)))
#price = np.array([x[0] for x in hist])
#h = np.array(hist)
#print(talib.SMA(price))
#print(len(h))
