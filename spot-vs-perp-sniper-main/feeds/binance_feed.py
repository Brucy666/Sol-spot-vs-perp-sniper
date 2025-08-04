# feeds/binance_feed.py

import asyncio
import websockets
import json

class BinanceCVDTracker:
    def __init__(self, spot_symbol="btcusdt", perp_symbol="btcusdt"):
        self.spot_symbol = spot_symbol
        self.perp_symbol = perp_symbol
        self.spot_cvd = 0.0
        self.perp_cvd = 0.0
        self.price = None

    async def connect(self):
        await asyncio.gather(
            self._connect_spot(),
            self._connect_perp()
        )

    async def _connect_spot(self):
        uri = f"wss://stream.binance.com:9443/ws/{self.spot_symbol}@aggTrade"
        async with websockets.connect(uri) as ws:
            async for msg in ws:
                await self._handle_spot_trade(json.loads(msg))

    async def _connect_perp(self):
        uri = f"wss://fstream.binance.com/ws/{self.perp_symbol}@aggTrade"
        async with websockets.connect(uri) as ws:
            async for msg in ws:
                await self._handle_perp_trade(json.loads(msg))

    async def _handle_spot_trade(self, msg):
        price = float(msg["p"])
        qty = float(msg["q"])
        is_buyer_maker = msg["m"]
        self.price = price
        if is_buyer_maker:
            self.spot_cvd -= qty
        else:
            self.spot_cvd += qty

    async def _handle_perp_trade(self, msg):
        price = float(msg["p"])
        qty = float(msg["q"])
        is_buyer_maker = msg["m"]
        self.price = price
        if is_buyer_maker:
            self.perp_cvd -= qty
        else:
            self.perp_cvd += qty

    def get_cvd(self):
        return {
            "spot": round(self.spot_cvd, 2),
            "perp": round(self.perp_cvd, 2),
            "price": self.price
        }
