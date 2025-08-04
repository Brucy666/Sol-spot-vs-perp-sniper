import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

class SentimentTracker:
    def __init__(self, symbol="SOL"):
        self.symbol = symbol.upper()
        self.api_key = os.getenv("LUNARCRUSH_API_KEY")
        self.last_score = 0
        self.last_mentions = 0
        self.last_change = 0

    def fetch_sentiment(self):
        url = f"https://api.lunarcrush.com/v2?data=assets&key={self.api_key}&symbol={self.symbol}"

        for attempt in range(3):
            try:
                res = requests.get(url, timeout=5)
                data = res.json()
                if "data" in data and isinstance(data["data"], list):
                    info = data["data"][0]
                    self.last_score = info.get("galaxy_score", 0)
                    self.last_mentions = info.get("social_volume", 0)
                    self.last_change = info.get("price_score", 0)
                    return
            except Exception as e:
                print(f"[Sentiment Fetch Error] Attempt {attempt+1}/3 → {e}")
                time.sleep(1)

        # Fallback to blank if unreachable
        self.last_score = 0
        self.last_mentions = 0
        self.last_change = 0

    def get_summary(self):
        badge = "📊"
        if self.last_score > 70:
            badge = "🔥"
        elif self.last_score > 50:
            badge = "⚡"

        return {
            "badge": badge,
            "galaxy_score": self.last_score,
            "mentions": self.last_mentions,
            "price_score": self.last_change
        }
