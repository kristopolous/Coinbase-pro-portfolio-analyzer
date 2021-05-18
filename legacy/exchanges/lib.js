const HTTP = require('http');
module.exports = {
  get: function(url, cb) {
    var parts = url.split('/'); 
    var options = {
      host: parts.shift(),
      path: '/' + parts.join('/')
    };
    var body = '';
    HTTP.get(options, function(request) {
      request.on('data', function(data) {
        body += data;
      });
      request.on('end', function() {
        cb(JSON.parse(body));
      });
    });
  },
  store: function(opts) {
  }
};
