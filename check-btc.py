#!/usr/bin/python3
import lib
import json
import secret
import requests

current = lib.btc_price(force=True)
name = 'btc-limits.json'

def notify(last, current, history):
    history = [str(x) for x in history]
    key = secret.mailgun[0]
    request_url = "%s/%s" % (secret.mailgun[1].strip('/'), 'messages')
    message = "BTC moved from {} to {}".format(last, current)
    request = requests.post(request_url, auth=('api', key), data={
       'from': secret.email[0],
       'to': secret.email[1],
       'subject': message,
       'text': "\n".join(history),
       'html': "<br>".join(history)
    })

with open(name, 'r') as json_data:
    d = json.load(json_data)
    range_list = d['range']
    last = d['last']

    for cutoff in range_list:
        if (current < cutoff and last > cutoff) or (current > cutoff and last < cutoff):
            notify(last, current, d['history'])
            break

    d['history'].append(current)
    d['history'] = d['history'][-20:]
    d['last'] = current

with open(name, 'w') as cache:
    json.dump(d, cache, indent=2)

