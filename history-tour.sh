#!/bin/bash

tmp=`mktemp`
curList=(`./balances.py 1`)
len=${#curList[*]}
ix=0
dir=1
while [ $ix -lt $len ]; do
  cur=${curList[$ix]}
  if [ $cur == 'BTC' ]; then
    (( ix += dir ))
    continue
  fi

  ./history.py $cur 60 > $tmp
  clear
  cat $tmp

  while [ 0 ]; do
    read -n 1 c
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

