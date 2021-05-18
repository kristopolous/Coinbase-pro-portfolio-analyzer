#!/usr/local/bin/node

var hit = require('./hitbtc-lib');

hit.currencyList(function(cm) {
  console.log(cm);
});
