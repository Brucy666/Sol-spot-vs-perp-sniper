import time
import requests

class OIFeed:
    def __init__(self, symbol="SOLUSDT"):
        self.symbol = symbol
        self.last_oi = None
        self.last_check = 0
        self.refresh_interval = 15  # seconds
        self.spike_threshold_pct = 1.0  # spike if OI changes > 1%

    def fetch_oi_from_bybit(self):
        try:
            url = f"https://api.bybit.com/v5/market/open-interest?category=linear&symbol={self.symbol}&interval=5"
            response = requests.get(url, timeout=5)
            data = response.json()

            oi_list = data.get("result", {}).get("list", [])
            if not oi_list:
                return None

            # Get latest Open Interest value
            latest_oi = float(oi_list[-1]["openInterest"])

            return latest_oi
        except Exception as e:
            print(f"[OI Feed Error] {e}")
            return None

    def get_snapshot(self):
        now = time.time()
        if now - self.last_check < self.refresh_interval:
            return self._format_oi_data(self.last_oi, 0)

        current_oi = self.fetch_oi_from_bybit()
        if current_oi is None:
            return self._format_oi_data(self.last_oi, 0)

        oi_delta = 0
        spike = False
        direction = "flat"
        bias = "neutral"

        if self.last_oi is not None:
            oi_delta = current_oi - self.last_oi
            percent_change = (abs(oi_delta) / self.last_oi) * 100 if self.last_oi else 0

            if percent_change >= self.spike_threshold_pct:
                spike = True
                direction = "up" if oi_delta > 0 else "down"
                bias = "long" if oi_delta > 0 else "short"

        self.last_oi = current_oi
        self.last_check = now

        return self._format_oi_data(current_oi, oi_delta, direction, spike, bias)

    def _format_oi_data(self, oi, delta, direction="flat", spike=False, bias="neutral"):
        return {
            "oi": round(oi, 2) if oi else None,
            "oi_delta": round(delta, 2),
            "direction": direction,
            "spike": spike,
            "bias": bias
        }
