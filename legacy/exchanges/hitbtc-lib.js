const WebSocket = require('ws');
const Lib = require('./lib');

module.exports = (function() {
  var _wsuri = "ws://api.hitbtc.com/api/2/ws";
  var _connection = new WebSocket(_wsuri);
  
  return {
    currencyList: function(cb) {
      Lib.get('api.hitbtc.com/api/2/public/currency', cb);
    },
    listen: function(cb) {
      _connection.on('open', function(m) {
        _connection.send(JSON.stringify({
          "method": "subscribeOrderbook",
          "params": {
            "symbol": "ETHBTC"
          },
          "id": 123
        }));
        _connection.on('message', cb);
      });
    }
  };
})();
