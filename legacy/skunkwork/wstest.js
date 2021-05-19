const WebSocket = require('ws');

var wsuri = "wss://api.poloniex.com";
var connection = new WebSocket(wsuri);

connection.on('open', function(m) {
  connection.send(JSON.stringify({
    "event": "subscribe",
    "channel": "BTC_XMR"
  }));
  connection.on('message', function(m) {
    console.log(m);
  });
});
