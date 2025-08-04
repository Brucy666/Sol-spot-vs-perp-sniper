import time
import hashlib

class AlertClusterBuffer:
    def __init__(self, buffer_window=60):
        self.last_signal_hash = None
        self.last_sent_time = 0
        self.buffer_window = buffer_window
        self.pending_signal = None
        self.pending_count = 0

    def should_send(self, signal_text, confidence, label):
        now = time.time()
        fingerprint = f"{signal_text}-{confidence}-{label}"
        signal_hash = hashlib.sha256(fingerprint.encode()).hexdigest()

        # Reset buffer if new signal or time expired
        if signal_hash != self.last_signal_hash or (now - self.last_sent_time) > self.buffer_window:
            self.last_signal_hash = signal_hash
            self.last_sent_time = now
            self.pending_signal = (signal_text, confidence, label)
            self.pending_count = 1
            return True  # Send first of group

        # Otherwise, increment and suppress alert
        self.pending_count += 1
        return False

    def get_buffer_info(self):
        return {
            "duplicates": self.pending_count,
            "last_sent": self.last_sent_time,
            "signal": self.pending_signal
        }
