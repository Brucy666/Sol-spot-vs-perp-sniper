import asyncio
import websockets
import json

class BTCReferenceFeed:
    def __init__(self):
        self.spot_cvd = 0
        self.perp_cvd = 0
        self.price = None

    async def connect(self):
        await asyncio.gather(
            self._connect_spot(),
            self._connect_perp()
        )

    async def _connect_spot(self):
        uri = "wss://stream.binance.com:9443/ws/btcusdt@aggTrade"
        async with websockets.connect(uri) as ws:
            async for msg in ws:
                await self._handle_spot(json.loads(msg))

    async def _connect_perp(self):
        uri = "wss://fstream.binance.com/ws/btcusdt@aggTrade"
        async with websockets.connect(uri) as ws:
            async for msg in ws:
                await self._handle_perp(json.loads(msg))

    async def _handle_spot(self, msg):
        qty = float(msg["q"])
        price = float(msg["p"])
        is_buyer_maker = msg["m"]
        self.price = price
        if is_buyer_maker:
            self.spot_cvd -= qty
        else:
            self.spot_cvd += qty

    async def _handle_perp(self, msg):
        qty = float(msg["q"])
        price = float(msg["p"])
        is_buyer_maker = msg["m"]
        self.price = price
        if is_buyer_maker:
            self.perp_cvd -= qty
        else:
            self.perp_cvd += qty

    def get_deltas(self):
        return {
            "btc_spot": round(self.spot_cvd, 2),
            "btc_perp": round(self.perp_cvd, 2),
            "price": self.price
        }
