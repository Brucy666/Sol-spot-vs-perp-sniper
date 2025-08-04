# sniper_executor.py

import json
import time
from datetime import datetime

class SniperExecutor:
    def __init__(self, score_threshold=7.0):
        self.last_trade_time = 0
        self.cooldown = 900  # 15 min cooldown
        self.score_threshold = score_threshold

    def should_execute(self, confidence, label):
        now = time.time()
        if confidence >= self.score_threshold and label == "spot_dominant":
            if now - self.last_trade_time > self.cooldown:
                return True
        return False

    def execute(self, signal, confidence, price, label):
        timestamp = datetime.utcnow().isoformat()
        self.last_trade_time = time.time()

        trade = {
            "timestamp": timestamp,
            "signal": signal,
            "confidence": confidence,
            "label": label,
            "executed_price": price
        }

        print("\n🎯 SNIPER EXECUTED:")
        print(json.dumps(trade, indent=2))

        with open("executed_trades.json", "a") as f:
            f.write(json.dumps(trade) + "\n")
