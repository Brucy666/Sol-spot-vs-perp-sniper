# feeds/bybit_feed.py

import asyncio
import websockets
import json

class BybitCVDTracker:
    def __init__(self, symbol="BTCUSDT"):
        self.symbol = symbol
        self.cvd = 0
        self.price = None

    async def connect(self):
        uri = "wss://stream.bybit.com/v5/public/linear"
        async with websockets.connect(uri) as ws:
            subscribe_msg = {
                "op": "subscribe",
                "args": [f"publicTrade.{self.symbol}"]
            }
            await ws.send(json.dumps(subscribe_msg))
            async for message in ws:
                await self.handle_message(json.loads(message))

    async def handle_message(self, msg):
        if "data" in msg and "topic" in msg:
            for trade in msg["data"]:
                side = trade["S"]  # "Buy" or "Sell"
                qty = float(trade["v"])
                price = float(trade["p"])
                self.price = price

                if side == "Buy":
                    self.cvd += qty
                elif side == "Sell":
                    self.cvd -= qty

    def get_cvd(self):
        return round(self.cvd, 2)

    def get_price(self):
        return self.price


if __name__ == "__main__":
    tracker = BybitCVDTracker()

    async def run():
        await tracker.connect()

    asyncio.run(run())
