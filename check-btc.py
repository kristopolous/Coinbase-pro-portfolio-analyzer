#!/usr/bin/python3
import lib
import json
import secret
import requests

current = lib.btc_price(force=True)
name = 'btc-limits.json'

def notify(last, current, history, direction):
    history = [str(x) for x in history]
    key = secret.mailgun[0]
    request_url = "%s/%s" % (secret.mailgun[1].strip('/'), 'messages')
    message = "BTC {} from {} to {}".format(direction, last, current)
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
    range_list = d['range']
    last = d['last']

    direction = False
    for cutoff in range_list:
        if current < cutoff and last > cutoff:
            direction = "down"

        if current > cutoff and last < cutoff:
            direction = "up"

        if direction:
            break

    perc = abs(last - current) / last
    if not direction and perc > 0.03:
        word = "up" if current > last else "down"
        direction = "{} {}%".format(word, perc * 100)

    if direction:
        notify(last, current, d['history'], direction)

    d['history'].append(current)
    d['history'] = d['history'][-20:]
    d['last'] = current

with open(name, 'w') as cache:
    json.dump(d, cache, indent=2)

