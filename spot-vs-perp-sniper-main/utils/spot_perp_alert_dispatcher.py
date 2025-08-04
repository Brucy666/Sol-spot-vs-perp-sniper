import time
import hashlib
from utils.discord_alert import send_discord_alert

class SpotPerpAlertDispatcher:
    def __init__(self, cooldown_seconds=900):
        self.last_signal_time = 0
        self.last_signal_hash = ""
        self.cooldown_seconds = cooldown_seconds  # default: 15 minutes

    async def maybe_alert(self, signal_text, confidence, label, deltas):
        now = time.time()
        signal_fingerprint = f"{signal_text}-{confidence}-{label}"
        signal_hash = hashlib.sha256(signal_fingerprint.encode()).hexdigest()

        # Decision rules
        is_dominant_trend = label in ["spot_dominant", "perp_dominant"]
        is_high_confidence = confidence >= 7
        is_not_duplicate = signal_hash != self.last_signal_hash
        is_outside_cooldown = (now - self.last_signal_time) > self.cooldown_seconds

        if is_dominant_trend and is_high_confidence and is_not_duplicate and is_outside_cooldown:
            direction = {
                "spot_dominant": "🟢 LONG",
                "perp_dominant": "🔴 SHORT"
            }.get(label, "⚠️ NEUTRAL")

            message = (
                f"🚨 **HIGH-CONFLUENCE SNIPER SIGNAL**\n"
                f"{signal_text}\n\n"
                f"🧠 Confidence Score: `{confidence}/10` → `{label}`\n"
                f"🎯 Suggested Trade: **{direction}**\n"
                f"📊 15m CVD Δ:\n"
                f"   • Coinbase: `{deltas['cb_cvd']}%`\n"
                f"   • Binance Spot: `{deltas['bin_spot']}%`\n"
                f"   • Binance Perp: `{deltas['bin_perp']}%`\n"
            )

            await send_discord_alert(message)
            self.last_signal_time = now
            self.last_signal_hash = signal_hash
