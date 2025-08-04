# feeds/coinbase_feed.py

import asyncio
import websockets
import json

class CoinbaseSpotCVD:
    def __init__(self, product_id="BTC-USD"):
        self.product_id = product_id
        self.cvd = 0
        self.last_price = None

    async def connect(self):
        uri = "wss://ws-feed.exchange.coinbase.com"
        async with websockets.connect(uri) as ws:
            await ws.send(json.dumps({
                "type": "subscribe",
                "channels": [{"name": "matches", "product_ids": [self.product_id]}]
            }))
            async for message in ws:
                await self.handle_message(json.loads(message))

    async def handle_message(self, msg):
        if msg["type"] == "match":
            side = msg["side"]
            size = float(msg["size"])
            price = float(msg["price"])
            self.last_price = price

            if side == "buy":
                self.cvd += size
            elif side == "sell":
                self.cvd -= size

    def get_cvd(self):
        return round(self.cvd, 2)

    def get_last_price(self):
        return self.last_price


if __name__ == "__main__":
    tracker = CoinbaseSpotCVD()

    async def run():
        await tracker.connect()

    asyncio.run(run())
