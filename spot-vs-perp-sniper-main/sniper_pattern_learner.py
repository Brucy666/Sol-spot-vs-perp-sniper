# sniper_pattern_learner.py

import os
import requests
from collections import defaultdict
from datetime import datetime

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def fetch_recent_snapshots(limit=100):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    url = f"{SUPABASE_URL}/rest/v1/cvd_snapshots?order=timestamp.desc&limit={limit}"

    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return resp.json()
    else:
        print(f"❌ Failed to fetch snapshots: {resp.status_code}")
        return []

def analyze_patterns(snapshots):
    pattern_counts = defaultdict(int)
    outcome_counts = defaultdict(int)
    trap_signals = 0
    breakout_signals = 0

    for snap in snapshots:
        signal = snap.get("signal", "UNKNOWN")
        outcome = snap.get("confirmed_outcome", "unknown")

        pattern_counts[signal] += 1
        outcome_counts[(signal, outcome)] += 1

        if outcome == "trap":
            trap_signals += 1
        elif outcome == "breakout":
            breakout_signals += 1

    print("\n🧠 SNIPER PATTERN LEARNER REPORT")
    print("--------------------------------------------------")
    for signal, count in pattern_counts.items():
        trap_rate = 0
        breakout_rate = 0
        if count > 0:
            trap_rate = (outcome_counts.get((signal, "trap"), 0) / count) * 100
            breakout_rate = (outcome_counts.get((signal, "breakout"), 0) / count) * 100

        print(f"🔍 Signal: {signal}")
        print(f"   - Occurrences: {count}")
        print(f"   - Trap Rate: {trap_rate:.1f}%")
        print(f"   - Breakout Rate: {breakout_rate:.1f}%\n")

    print(f"📊 Total Trap Signals: {trap_signals}")
    print(f"📈 Total Breakout Signals: {breakout_signals}")
    print("--------------------------------------------------")

if __name__ == "__main__":
    snapshots = fetch_recent_snapshots(limit=250)
    if snapshots:
        analyze_patterns(snapshots)
    else:
        print("⚠️ No data available to analyze.")
