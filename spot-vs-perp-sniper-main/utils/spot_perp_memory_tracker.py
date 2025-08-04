# utils/spot_perp_memory_tracker.py

import time
from collections import deque

class SpotPerpMemoryTracker:
    def __init__(self):
        self.memory_15m = deque()
        self.memory_60m = deque()
        self.max_age_15m = 15 * 60
        self.max_age_60m = 60 * 60

    def update(self, cb_cvd, bin_spot, bin_perp):
        now = time.time()
        point = (now, cb_cvd, bin_spot, bin_perp)
        self.memory_15m.append(point)
        self.memory_60m.append(point)
        self._cleanup(now)

    def _cleanup(self, now):
        while self.memory_15m and now - self.memory_15m[0][0] > self.max_age_15m:
            self.memory_15m.popleft()
        while self.memory_60m and now - self.memory_60m[0][0] > self.max_age_60m:
            self.memory_60m.popleft()

    def get_rolling_deltas(self):
        return {
            "15m": self._calculate_deltas(self.memory_15m),
            "60m": self._calculate_deltas(self.memory_60m)
        }

    def _calculate_deltas(self, memory):
        if len(memory) < 2:
            return {"cb_cvd": 0, "bin_spot": 0, "bin_perp": 0}

        start = memory[0]
        end = memory[-1]

        def pct_change(a, b):
            return round(((b - a) / abs(a)) * 100, 2) if a != 0 else 0

        return {
            "cb_cvd": pct_change(start[1], end[1]),
            "bin_spot": pct_change(start[2], end[2]),
            "bin_perp": pct_change(start[3], end[3])
        }
