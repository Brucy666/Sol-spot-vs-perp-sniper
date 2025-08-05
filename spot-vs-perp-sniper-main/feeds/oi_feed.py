import time
import requests

class OIFeed:
    def __init__(self, symbol="SOLUSDT"):
        self.symbol = symbol
        self.last_oi = None
        self.last_check = 0
        self.refresh_interval = 15  # seconds
        self.spike_threshold_pct = 1.0  # % change threshold to count as spike

    def fetch_oi_from_bybit(self):
        try:
            url = f"https://api.bybit.com/v5/market/open-interest?category=linear&symbol={self.symbol}&interval=15"
            response = requests.get(url, timeout=5)
            data = response.json()

            print(f"[OI DEBUG] Raw API response: {data}")

            oi_list = data.get("result", {}).get("list", [])
            if not oi_list:
                print("[OI DEBUG] No OI data returned.")
                return None

            latest_entry = oi_list[-1]
            latest_oi = latest_entry.get("openInterest")

            if latest_oi is None:
                print("[OI DEBUG] Missing 'openInterest' field in latest entry.")
                return None

            return float(latest_oi)

        except Exception as e:
            print(f"[OI ERROR] {e}")
            return None

    def get_snapshot(self):
        now = time.time()
        if now - self.last_check < self.refresh_interval:
            return self._format_oi_data(self.last_oi, 0)

        current_oi = self.fetch_oi_from_bybit()
        if current_oi is None:
            return self._format_oi_data(None, 0)

        # Default values
        delta = 0
        direction = "flat"
        spike = False
        bias = "neutral"

        if self.last_oi is not None:
            delta = current_oi - self.last_oi
            percent_change = (abs(delta) / self.last_oi) * 100 if self.last_oi != 0 else 0

            if percent_change >= self.spike_threshold_pct:
                spike = True
                direction = "up" if delta > 0 else "down"
                bias = "long" if delta > 0 else "short"

        self.last_oi = current_oi
        self.last_check = now

        return self._format_oi_data(current_oi, delta, direction, spike, bias)

    def _format_oi_data(self, oi, delta, direction="flat", spike=False, bias="neutral"):
        return {
            "oi": round(oi, 2) if oi else None,
            "oi_delta": round(delta, 2),
            "direction": direction,
            "spike": spike,
            "bias": bias
        }
