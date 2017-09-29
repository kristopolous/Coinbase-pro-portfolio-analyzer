#!/bin/bash

tmp=`mktemp`
for i in `./balances.py 1`; do
  if [ $i == 'BTC' ]; then
    continue
  fi

  ./history.py $i 60 > $tmp
  clear
  cat $tmp
  sleep 3
done

