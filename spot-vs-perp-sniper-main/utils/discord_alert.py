import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_SOL")  # Set this in .env

async def send_discord_alert(message: str):
    if not DISCORD_WEBHOOK_URL:
        print("❌ No Discord webhook set for SOL sniper alerts.")
        return

    async with aiohttp.ClientSession() as session:
        payload = {"content": message}
        async with session.post(DISCORD_WEBHOOK_URL, json=payload) as resp:
            if resp.status != 204:
                print(f"❌ Discord webhook failed with status: {resp.status}")
            else:
                print("✅ SOL sniper alert sent to Discord.")
