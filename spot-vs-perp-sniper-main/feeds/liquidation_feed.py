import time
import requests

class LiquidationFeed:
    def __init__(self, symbol="SOLUSDT"):
        self.symbol = symbol
        self.last_check = 0
        self.refresh_interval = 15  # seconds
        self.last_liqs = {'longs': 0, 'shorts': 0}
        self.spike_threshold = 1.5  # 150% increase = spike

    def fetch_bybit_liquidations(self):
        try:
            url = f"https://api.bybit.com/v5/market/liquidation?category=linear&symbol={self.symbol}&limit=50"
            response = requests.get(url, timeout=5)
            data = response.json()

            liq_list = data.get("result", {}).get("list", [])
            print(f"[LIQ DEBUG] Raw liq list (last 50): {liq_list}")

            longs = 0
            shorts = 0

            for liq in liq_list:
                side = liq.get("side")
                qty = float(liq.get("qty", 0))
                if side == "Buy":
                    shorts += qty  # shorts liquidated
                elif side == "Sell":
                    longs += qty  # longs liquidated

            return longs, shorts

        except Exception as e:
            print(f"[LIQ ERROR] Failed to fetch liquidations: {e}")
            return 0, 0

    def get_liquidation_snapshot(self):
        now = time.time()
        if now - self.last_check < self.refresh_interval:
            return self._format_liq_data(**self.last_liqs)

        longs, shorts = self.fetch_bybit_liquidations()
        self.last_check = now

        previous_total = self.last_liqs['longs'] + self.last_liqs['shorts']
        current_total = longs + shorts

        spike = False
        if previous_total > 0 and current_total > previous_total * self.spike_threshold:
            spike = True

        # Save current values for next comparison
        self.last_liqs = {'longs': longs, 'shorts': shorts}

        return self._format_liq_data(longs, shorts, spike)

    def _format_liq_data(self, longs=0, shorts=0, spike=False):
        dominant = "longs" if longs > shorts else "shorts"
        bias = "short" if dominant == "longs" else "long"

        # Prevent fake bias if both values are zero
        if longs == 0 and shorts == 0:
            dominant = "none"
            bias = "neutral"

        return {
            "longs": round(longs, 2),
            "shorts": round(shorts, 2),
            "dominant": dominant,
            "bias": bias,
            "spike": spike
        }
