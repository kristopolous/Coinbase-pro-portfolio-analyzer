#!/bin/bash
cd cache
set +x
for i in *; do
  redis-cli hset 'coinhash' $i "$(cat $i)"
done
   
