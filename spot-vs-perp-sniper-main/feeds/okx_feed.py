# feeds/okx_feed.py

import asyncio
import websockets
import json

class OKXCVDTracker:
    def __init__(self, instId="BTC-USDT-SWAP"):
        self.instId = instId
        self.cvd = 0
        self.price = None

    async def connect(self):
        uri = "wss://ws.okx.com:8443/ws/v5/public"
        async with websockets.connect(uri) as ws:
            sub_msg = {
                "op": "subscribe",
                "args": [{
                    "channel": "trades",
                    "instId": self.instId
                }]
            }
            await ws.send(json.dumps(sub_msg))
            async for message in ws:
                await self.handle_message(json.loads(message))

    async def handle_message(self, msg):
        if "data" in msg:
            for trade in msg["data"]:
                side = trade["side"]  # "buy" or "sell"
                sz = float(trade["sz"])
                px = float(trade["px"])
                self.price = px

                if side == "buy":
                    self.cvd += sz
                elif side == "sell":
                    self.cvd -= sz

    def get_cvd(self):
        return round(self.cvd, 2)

    def get_price(self):
        return self.price


if __name__ == "__main__":
    tracker = OKXCVDTracker()

    async def run():
        await tracker.connect()

    asyncio.run(run())
