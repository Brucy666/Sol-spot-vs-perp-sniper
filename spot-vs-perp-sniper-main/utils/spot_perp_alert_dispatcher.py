import time
import hashlib
from utils.discord_alert import send_discord_alert

class SpotPerpAlertDispatcher:
    def __init__(self, cooldown_seconds=300):  # 🧠 Reduced from 900 → 300 for SOL volatility
        self.last_signal_time = 0
        self.last_signal_hash = ""
        self.cooldown_seconds = cooldown_seconds

    async def maybe_alert(self, signal_text, confidence, label, deltas, force_test=False):
        now = time.time()
        signal_fingerprint = f"{signal_text}-{confidence}-{label}"
        signal_hash = hashlib.sha256(signal_fingerprint.encode()).hexdigest()

        # === TEST MODE ===
        if force_test:
            message = (
                f"🧪 **TEST SNIPER SIGNAL (SOL)**\n"
                f"{signal_text}\n\n"
                f"🧠 Confidence Score: `{confidence}/10` → `{label}`\n"
                f"🎯 Suggested Trade: **🟢 LONG (Test Mode)**\n"
                f"📊 Simulated 15m CVD Δ:\n"
                f"   • Coinbase: `{deltas.get('cb_cvd', 'n/a')}%`\n"
                f"   • Binance Spot: `{deltas.get('bin_spot', 'n/a')}%`\n"
                f"   • Binance Perp: `{deltas.get('bin_perp', 'n/a')}%`\n"
            )
            await send_discord_alert(message)
            print("✅ [TEST ALERT SENT]")
            return

        # === Real Alert Conditions ===
        is_dominant_trend = label in ["spot_dominant", "perp_dominant"]
        is_high_confidence = confidence >= 7
        is_not_duplicate = signal_hash != self.last_signal_hash
        is_outside_cooldown = (now - self.last_signal_time) > self.cooldown_seconds

        # === Direction override based on trap type ===
        if "SHORT trap" in signal_text or "bull trap" in signal_text:
            direction = "🔴 SHORT"
        elif "LONG trap" in signal_text or "short squeeze" in signal_text:
            direction = "🟢 LONG"
        else:
            direction = {
                "spot_dominant": "🟢 LONG",
                "perp_dominant": "🔴 SHORT"
            }.get(label, "⚠️ NEUTRAL")

        if is_dominant_trend and is_high_confidence and is_not_duplicate and is_outside_cooldown:
            message = (
                f"📈 **HIGH-CONFLUENCE SNIPER SIGNAL (SOL)**\n"
                f"{signal_text}\n\n"
                f"🧠 Confidence Score: `{confidence}/10` → `{label}`\n"
                f"🎯 Suggested Trade: **{direction}**\n"
                f"📊 15m CVD Δ Breakdown:\n"
                f"   • Coinbase (SOL-USD): `{deltas.get('cb_cvd', 'n/a')}%`\n"
                f"   • Binance Spot: `{deltas.get('bin_spot', 'n/a')}%`\n"
                f"   • Binance Perp: `{deltas.get('bin_perp', 'n/a')}%`\n"
            )

            await send_discord_alert(message)
            self.last_signal_time = now
            self.last_signal_hash = signal_hash
