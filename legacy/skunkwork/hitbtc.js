const WebSocket = require('ws');

var wsuri = "ws://api.hitbtc.com/api/2/ws";
var connection = new WebSocket(wsuri);

connection.on('open', function(m) {
  connection.send(JSON.stringify({
    "method": "subscribeOrderbook",
    "params": {
      "symbol": "ETHBTC"
    },
    "id": 123
  }));
  connection.on('message', function(m) {
    console.log(m);
  });
});
