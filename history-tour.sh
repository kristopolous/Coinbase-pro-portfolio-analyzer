#!/bin/bash

tmp=`mktemp`
curList=(`./balances.py -l -g .005`)
len=${#curList[*]}
ix=0
dir=1
range=80
btc=0
btcValue=1000
makebtc() {
  dir=0
  btc=$(( 100000 + btcValue ))
  btc=0.${btc/#1/}
}

while [ $ix -lt $len ]; do
  cur=${curList[$ix]}
  if [ $cur == 'BTC' ]; then
    (( ix += dir ))
    continue
  fi

  ./history.py $cur $range $btc > $tmp
  clear
  cat $tmp

  while [ 0 ]; do
    read -n 1 c
    if [ $c == 'k' ]; then
      btcValue=$(( btcValue * 10 / 13 )) 
      makebtc
      break
    fi

    if [ $c == 'l' ]; then
      btcValue=$(( btcValue * 13 / 10 )) 
      makebtc
      break
    fi

    if [ $c == 'o' ]; then
      dir=0
      range=$(( range - 1 ))
      break
    fi
    if [ $c == 'p' ]; then
      dir=0
      range=$(( range + 1 ))
      break
    fi
    if [ $c == '.' ]; then
      dir=1
      break
    fi
    if [ $c == ',' ]; then
      dir=-1
      break
    fi
    [ $c == 'q' ] && exit
  done

  (( ix += dir ))

  if [ $ix -eq $len ]; then
    ix=0
  fi
  if [ $ix -lt "0" ]; then
    ix=$(( len - 1 ))
    echo $ix
  fi
done

