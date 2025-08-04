# utils/multi_tf_memory.py

import time
from collections import deque

class MultiTFMemory:
    def __init__(self):
        self.windows = {
            "5m": {"max_age": 5 * 60, "memory": deque()},
            "15m": {"max_age": 15 * 60, "memory": deque()},
            "1h": {"max_age": 60 * 60, "memory": deque()}
        }

    def update(self, cb_cvd, bin_spot, bin_perp):
        now = time.time()
        point = (now, cb_cvd, bin_spot, bin_perp)

        for tf in self.windows:
            self.windows[tf]["memory"].append(point)
            self._cleanup(tf, now)

    def _cleanup(self, tf, now):
        max_age = self.windows[tf]["max_age"]
        memory = self.windows[tf]["memory"]
        while memory and now - memory[0][0] > max_age:
            memory.popleft()

    def get_all_deltas(self):
        result = {}
        for tf, data in self.windows.items():
            result[tf] = self._calculate_deltas(data["memory"])
        return result

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
