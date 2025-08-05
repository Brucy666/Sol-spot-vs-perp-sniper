import time
import requests

class LiquidationFeed:
    def __init__(self):
        self.last_check = 0
        self.refresh_interval = 15  # seconds
        self.last_liqs = {'longs': 0, 'shorts': 0}
        self.spike_threshold = 1.5  # Multiplier for spike detection

    def fetch_bybit_liquidations(self, symbol="SOLUSDT"):
        try:
            url = f"https://api.bybit.com/v5/market/liquidation?category=linear&symbol={symbol}&limit=50"
            response = requests.get(url, timeout=5)
            data = response.json()

            longs = 0
            shorts = 0

            for liq in data.get("result", {}).get("list", []):
                side = liq.get("side")
                vol = float(liq.get("qty", 0))
                if side == "Buy":
                    shorts += vol  # short position got liquidated
                elif side == "Sell":
                    longs += vol  # long position got liquidated

            return longs, shorts

        except Exception as e:
            print(f"[Liq Feed Error] {e}")
            return 0, 0

    def get_liquidation_snapshot(self):
        now = time.time()
        if now - self.last_check < self.refresh_interval:
            return self._format_liq_data(*self.last_liqs)

        longs, shorts = self.fetch_bybit_liquidations()
        self.last_check = now
        self.last_liqs = {'longs': longs, 'shorts': shorts}
        return self._format_liq_data(longs, shorts)

    def _format_liq_data(self, longs, shorts):
        dominant = "longs" if longs > shorts else "shorts"
        bias = "short" if dominant == "longs" else "long"

        spike = False
        total_new_liq = longs + shorts
        total_old_liq = self.last_liqs['longs'] + self.last_liqs['shorts']
        if total_old_liq > 0 and total_new_liq > total_old_liq * self.spike_threshold:
            spike = True

        return {
            'longs': round(longs, 2),
            'shorts': round(shorts, 2),
            'dominant': dominant,
            'bias': bias,
            'spike': spike
        }
