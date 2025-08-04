# utils/cvd_snapshot_writer.py

import os
import requests
from datetime import datetime

# Load Supabase credentials from environment
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def write_snapshot_to_supabase(snapshot):
    # Guard clause if env vars missing
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Missing Supabase credentials. Check SUPABASE_URL and SUPABASE_KEY in your .env or Railway variables.")
        return

    # Prepare payload
    payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "exchange": snapshot.get("exchange", "unknown"),
        "spot_cvd": snapshot.get("spot_cvd", 0.0),
        "perp_cvd": snapshot.get("perp_cvd", 0.0),
        "price": snapshot.get("price", 0.0),
        "signal": snapshot.get("signal", "unspecified"),
        "confirmed_outcome": snapshot.get("confirmed_outcome", None)
    }

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

    url = f"{SUPABASE_URL}/rest/v1/cvd_snapshots"

    try:
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 201:
            print("✅ Snapshot saved to Supabase.")
        else:
            print(f"❌ Supabase write failed.")
            print(f"    Status: {response.status_code}")
            print(f"    Response: {response.text}")

    except Exception as e:
        print("❌ Exception during Supabase write:")
        print(str(e))
