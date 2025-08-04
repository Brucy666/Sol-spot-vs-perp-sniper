# utils/memory_logger.py

import json
from datetime import datetime

MEMORY_FILE = "cvd_memory.json"

def log_snapshot(snapshot):
    snapshot["timestamp"] = datetime.utcnow().isoformat()

    try:
        with open(MEMORY_FILE, "r") as f:
            history = json.load(f)
    except FileNotFoundError:
        history = []

    history.append(snapshot)

    # Limit file size
    history = history[-500:]

    with open(MEMORY_FILE, "w") as f:
        json.dump(history, f, indent=2)
