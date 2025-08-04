import os
import requests
from datetime import datetime

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def log_sniper_alert(alert):
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("[X] Missing SUPABASE_URL or SUPABASE_KEY in environment.")
        return

    url = f"{SUPABASE_URL}/rest/v1/sniper_alerts"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

    data = {
        "timestamp": datetime.utcnow().isoformat(),
        "signal": alert.get("signal"),
        "direction": alert.get("direction"),
        "confidence_score": alert.get("confidence"),
        "bias_label": alert.get("label"),
        "cb_cvd": alert.get("cb_cvd"),
        "bin_spot": alert.get("bin_spot"),
        "bin_perp": alert.get("bin_perp"),
        "triggered_price": alert.get("price"),
        # "resolution_time": None,
        # "pnl_percent": None,
        # "outcome": None
    }

    try:
        res = requests.post(url, headers=headers, json=data)
        if res.status_code not in [200, 201, 204]:
            print("[X] Supabase insert failed:", res.status_code, res.text)
        else:
            print("[✓] Sniper alert saved to Supabase.")
    except Exception as e:
        print("[X] Error logging sniper alert:", e)
