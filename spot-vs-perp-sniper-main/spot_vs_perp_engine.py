import asyncio
import os
import time
import hashlib
from dotenv import load_dotenv

from feeds.coinbase_feed import CoinbaseSpotCVD
from feeds.binance_feed import BinanceCVDTracker
from feeds.bybit_feed import BybitCVDTracker
from feeds.okx_feed import OKXCVDTracker
from feeds.funding_feed import FundingRateTracker
from feeds.delta_spike_feed import DeltaSpikeTracker
from feeds.btc_reference_feed import BTCReferenceFeed

from utils.alert_cluster_buffer import AlertClusterBuffer
from utils.discord_alert import send_discord_alert
from utils.memory_logger import log_snapshot
from utils.cvd_snapshot_writer import write_snapshot_to_supabase
from utils.multi_tf_memory import MultiTFMemory
from utils.spot_perp_alert_dispatcher import SpotPerpAlertDispatcher
from utils.spot_perp_scorer import score_spot_perp_confluence_multi
from sniper_executor import SniperExecutor

load_dotenv()
FORCE_TEST_ALERT = os.getenv("FORCE_TEST_ALERT", "false").lower() == "true"

class SpotVsPerpEngine:
    def __init__(self):
        self.coinbase = CoinbaseSpotCVD(product_id="SOL-USD")
        self.binance = BinanceCVDTracker(spot_symbol="SOLUSDT", perp_symbol="SOLUSDT")
        self.bybit = BybitCVDTracker(symbol="SOLUSDT")
        self.okx = OKXCVDTracker(instId="SOL-USDT-SWAP")
        self.btc = BTCReferenceFeed()
        self.funding_tracker = FundingRateTracker()
        self.delta_tracker = DeltaSpikeTracker()

        self.memory = MultiTFMemory()
        self.alert_buffer = AlertClusterBuffer(buffer_window=60)
        self.alert_dispatcher = SpotPerpAlertDispatcher()
        self.executor = SniperExecutor()

        self.signal_cooldown_seconds = 300
        self.last_signal = None
        self.last_signal_time = 0
        self.last_signal_hash = ""

    async def run(self):
        await asyncio.gather(
            self.coinbase.connect(),
            self.binance.connect(),
            self.bybit.connect(),
            self.okx.connect(),
            self.btc.connect(),
            self.monitor()
        )

    async def monitor(self):
        while True:
            try:
                cb_cvd = self.coinbase.get_cvd()
                cb_price = self.coinbase.get_last_price()

                bin_data = self.binance.get_cvd()
                bin_spot = bin_data["spot"]
                bin_perp = bin_data["perp"]
                bin_price = bin_data["price"]

                bybit_cvd = self.bybit.get_cvd()
                bybit_price = self.bybit.get_price()

                okx_cvd = self.okx.get_cvd()
                okx_price = self.okx.get_price()

                await self.funding_tracker.update()
                self.delta_tracker.add_tick(bin_perp)
                spike_data = self.delta_tracker.check_spike()

                btc_data = self.btc.get_deltas()
                btc_spot = btc_data["btc_spot"]
                btc_perp = btc_data["btc_perp"]
                btc_price = btc_data["price"]

                self.memory.update(cb_cvd, bin_spot, bin_perp)
                deltas = self.memory.get_all_deltas()
                scored = score_spot_perp_confluence_multi(deltas)
                confidence = scored["score"]
                bias_label = scored["label"]

                signal = "📊 No clear bias"

                if bin_perp > 0 and cb_cvd < 0 and bin_spot < 0:
                    signal = "🔻 Perp pump + spot fade — bull trap forming (short opportunity)"

                elif self.funding_tracker.get_average() < -0.01 and cb_cvd > 0:
                    signal = "💥 Negative funding + Spot buying — short squeeze trap"

                elif spike_data["spike"] and cb_cvd < 0:
                    signal = "🔥 Perp delta spike + Spot selling — buyer trap likely"

                elif cb_cvd > 0 and bin_spot > 0 and bin_perp < 0 and btc_spot > 0:
                    signal = "✅ Spot-led move with BTC confirmation — strong demand"

                elif cb_cvd > 0 and bin_spot > 0 and btc_spot < 0:
                    signal = "⚠️ SOL spot strong but BTC fading — possible local top"

                elif bin_perp > 0 and cb_cvd < 0 and bin_spot <= 0:
                    signal = "🚨 Perp-led pump — no spot participation (trap)"

                elif bybit_cvd > 0 and bin_perp < 0:
                    signal = "⚠️ Bybit retail buying, Binance fading — exit risk"

                elif okx_cvd < 0 and bin_perp > 0:
                    signal = "🟡 OKX selling, Binance buying — Asia dump risk"

                elif cb_cvd > 0 and bin_spot < 0:
                    signal = "🕣 Coinbase buying, Binance Spot selling — divergence"

                print("\n==================== SPOT vs PERP REPORT (SOL) ====================")
                print(f"🟩 CB Spot CVD: {cb_cvd} | Price: {cb_price}")
                print(f"🗭 Binance Spot CVD: {bin_spot}")
                print(f"🔳 Binance Perp CVD: {bin_perp} | Price: {bin_price}")
                print(f"🕧 Bybit Perp CVD: {bybit_cvd} | Price: {bybit_price}")
                print(f"🕪 OKX CVD: {okx_cvd} | Price: {okx_price}")
                print(f"📉 Funding Rate: {self.funding_tracker.get_average()}%")
                print(f"⚡ Delta Spike: {spike_data}")
                print(f"🔗 BTC Spot: {btc_spot} | BTC Perp: {btc_perp} | Price: {btc_price}")
                print(f"\n🧠 Signal: {signal}")
                for tf, tf_deltas in deltas.items():
                    print(f"🕒 {tf} Δ → CB: {tf_deltas['cb_cvd']}% | Spot: {tf_deltas['bin_spot']}% | Perp: {tf_deltas['bin_perp']}%")
                print(f"💡 Confidence: {confidence}/10 → {bias_label.upper()}")
                print("====================================================================")

                snapshot = {
                    "exchange": "multi",
                    "signal": signal,
                    "confidence": confidence,
                    "bias": bias_label,
                    "price": bin_price or cb_price or bybit_price or okx_price,
                    "funding_rate": self.funding_tracker.get_average(),
                    "spike": spike_data["spike"],
                    "spike_delta": spike_data["net_delta"],
                    "btc_spot": btc_spot,
                    "btc_perp": btc_perp
                }

                log_snapshot(snapshot)

                now = time.time()
                signal_signature = f"{signal}-{bin_spot}-{cb_cvd}-{bin_perp}"
                signal_hash = hashlib.sha256(signal_signature.encode()).hexdigest()

                is_unique = signal_hash != self.last_signal_hash
                is_cooldown = now - self.last_signal_time > self.signal_cooldown_seconds
                is_meaningful = any(tag in signal for tag in ["✅", "🚨", "⚠️", "🟡", "🕣", "💥", "🔥", "🔻"])

                if is_unique and is_cooldown and is_meaningful:
                    write_snapshot_to_supabase(snapshot)
                    self.last_signal = signal
                    self.last_signal_time = now
                    self.last_signal_hash = signal_hash

                if self.alert_buffer.should_send(signal, confidence, bias_label):
                    await self.alert_dispatcher.maybe_alert(
                        signal,
                        confidence,
                        bias_label,
                        deltas.get("15m", {}),
                        force_test=FORCE_TEST_ALERT
                    )

                if self.executor.should_execute(confidence, bias_label):
                    self.executor.execute(signal, confidence, bin_price or cb_price, bias_label)

            except Exception as e:
                print(f"[ERROR] Monitor loop failed: {e}")

            await asyncio.sleep(5)

if __name__ == "__main__":
    engine = SpotVsPerpEngine()
    asyncio.run(engine.run())
