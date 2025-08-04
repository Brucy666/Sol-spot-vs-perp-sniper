import requests
import asyncio

class FundingRateTracker:
    def __init__(self):
        self.bybit_funding = 0.0
        self.binance_funding = 0.0

    async def update(self):
        await asyncio.gather(
            self.fetch_bybit(),
            self.fetch_binance()
        )

    async def fetch_bybit(self):
        try:
            url = "https://api.bybit.com/v2/public/funding/prev-funding-rate?symbol=SOLUSDT"
            res = requests.get(url, timeout=5)
            data = res.json()
            if "result" in data:
                self.bybit_funding = float(data["result"]["funding_rate"]) * 100  # convert to %
        except Exception as e:
            print(f"[Bybit Funding Error] {e}")

    async def fetch_binance(self):
        try:
            url = "https://fapi.binance.com/fapi/v1/fundingRate?symbol=SOLUSDT&limit=1"
            res = requests.get(url, timeout=5)
            data = res.json()
            if isinstance(data, list) and len(data) > 0:
                self.binance_funding = float(data[0]["fundingRate"]) * 100
        except Exception as e:
            print(f"[Binance Funding Error] {e}")

    def get_average(self):
        rates = [self.bybit_funding, self.binance_funding]
        valid = [r for r in rates if r != 0]
        return round(sum(valid) / len(valid), 4) if valid else 0.0
