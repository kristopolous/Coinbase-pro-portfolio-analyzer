#!/usr/bin/python3
import lib
import time
import json
import secret
import requests

cutoff = 0.0001
current = lib.btc_price(force=True)
name = 'btc-limits.json'

def notify(last, current, history, direction):
    history = [str(x) for x in history]
    key = secret.mailgun[0]
    request_url = "%s/%s" % (secret.mailgun[1].strip('/'), 'messages')
    message = "{:.2f}..{:.2f} {}".format(last, current, direction)
    request = requests.post(request_url, auth=('api', key), data={
       'from': secret.email[0],
       'to': secret.email[1],
       'subject': message,
       'text': "\n".join(history),
       'html': "<br>".join(history)
    })
    print(message)

with open(name, 'r') as json_data:
    d = json.load(json_data)
    last = d['last']
    lastts = d['lastts']
    now = time.time()
    delta = "{:.2f}m".format((now - lastts) / 60)

    direction = False
    ratio = current / last
    
    if ratio < (1 - cutoff):
        direction = "{} -{:.2f}%".format(delta, 100 * (1 - ratio))

    if ratio > (1 + cutoff):
        direction = "{} +{:.2f}%".format(delta, 100 * (ratio - 1))

    if current > 1.005 * d['high']:
        direction = "new high"
        d['high'] = current

    if current < 0.995 * d['low']:
        direction = "new low"
        d['low'] = current

    if direction:
        notify(last, current, d['history'], direction)
        d['last'] = current
        d['lastts'] = now
    else:
        print("{}..{} ({:.5f} {:.2f})".format(last, current, current - last, 100 * ratio))

    d['history'].append([time.strftime("%Y-%m-%d %H:%M:%S"), current])
    d['history'] = d['history'][-250:]
    d['prev'] = current

with open(name, 'w') as cache:
    json.dump(d, cache, indent=2)

