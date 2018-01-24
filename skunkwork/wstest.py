#!/usr/bin/python3
import asyncio
import websockets
import json

async def hello():
    async with websockets.client.connect('wss://api.poloniex.com', sslopt={"cert_reqs": ssl.CERT_NONE}) as ws:
        await ws.send("hello")
        greeting = await ws.recv()
        print(greeting)
        print(ws)
        """
        await ws.send(json.dumps({
            "event": "subscribe",
            "channel": "BTC_XMR"
        }))

        greeting = await websocket.recv()
        print(greeting)
        """

asyncio.get_event_loop().run_until_complete(hello())
