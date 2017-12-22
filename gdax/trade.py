#!/usr/bin/python3
import secret
import gdax

auth_client = gdax.AuthenticatedClient(secret.key, secret.b64secret, secret.passphrase)

buyList = [
    ["10", "1"],
    ["1", "10"],
    ["0.1", "100"],
    ["0.1", "500"],
    ["0.1", "1000"],
    ["0.05", "2000"],
    ["0.05", "2500"]
]

while True:
    for pair in buyList:
        res = auth_client.buy(price=pair[1], size=pair[0], product_id="BCH-USD", post_only=True)
        print(res)
        res = auth_client.buy(price=pair[1], size=pair[0], product_id="BCH-USD")
        print(res)
