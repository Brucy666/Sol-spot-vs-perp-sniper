import collections
import time

class DeltaSpikeTracker:
    def __init__(self, max_window_seconds=30):
        self.recent_deltas = collections.deque(maxlen=100)
        self.last_spike_time = 0
        self.spike_threshold = 1000  # Adjust based on volatility
        self.time_window = max_window_seconds

    def add_tick(self, delta_value):
        timestamp = time.time()
        self.recent_deltas.append((timestamp, delta_value))

    def check_spike(self):
        now = time.time()
        recent = [v for t, v in self.recent_deltas if now - t < self.time_window]
        net = sum(recent)
        is_spike = abs(net) > self.spike_threshold
        if is_spike:
            self.last_spike_time = now
        return {
            "spike": is_spike,
            "net_delta": net,
            "count": len(recent),
            "since_last": now - self.last_spike_time
        }
