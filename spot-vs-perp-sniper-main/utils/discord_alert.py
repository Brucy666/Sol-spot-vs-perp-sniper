# utils/discord_alert.py

import aiohttp
import os

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_SPOT_PERP")  # Set this in .env

async def send_discord_alert(message: str):
    if not DISCORD_WEBHOOK_URL:
        print("❌ No Discord webhook set for Spot vs Perp alerts.")
        return

    async with aiohttp.ClientSession() as session:
        payload = {"content": message}
        async with session.post(DISCORD_WEBHOOK_URL, json=payload) as resp:
            if resp.status != 204:
                print(f"❌ Discord webhook failed with status: {resp.status}")
