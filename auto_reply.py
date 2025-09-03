# -----------------------------
# Required imports
import os
import time
import random
import asyncio
from datetime import datetime
from telethon import TelegramClient, events
from dotenv import load_dotenv
# -----------------------------

# -----------------------------
# Load environment variables from .env
load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
phone = os.getenv("PHONE")
# -----------------------------

client = TelegramClient("session", api_id, api_hash)

# -----------------------------
# Auto-reply messages
DAY_REPLIES = [
    "Hey! I'm offline right now 🙂",
    "Can't talk at the moment, will reply later!",
    "BRB 😉 Talk soon!",
    "I'm away from Telegram, will get back to you."
]

NIGHT_REPLIES = [
    "Abhi so raha hu, baad me reply karunga 🙂"
]

OFFENSIVE_WORDS = ["gali1", "gali2"]  # Add offensive words

LIMIT_SECONDS = 3600  # 1 hour cooldown
NIGHT_START = 21      # 9 PM
NIGHT_END = 7         # 7 AM

# -----------------------------
# Trackers
last_reply_time = {}
replied_messages = {}
message_count = {}
warning_sent = {}

# -----------------------------
def get_current_reply():
    hour = datetime.now().hour
    if NIGHT_START <= hour or hour < NIGHT_END:
        return random.choice(NIGHT_REPLIES)
    else:
        return random.choice(DAY_REPLIES)

# -----------------------------
@client.on(events.NewMessage(incoming=True))
async def handler(event):
    if event.is_private:
        chat_id = event.chat_id
        now_time = time.time()
        msg_text = event.raw_text.lower()

        # Offensive message check
        if any(word in msg_text for word in OFFENSIVE_WORDS):
            await client.delete_messages(chat_id, event.id, revoke=True)
            return

        # Thumbs up react
        await event.react("👍")

        # Spam detection
        count = message_count.get(chat_id, 0) + 1
        message_count[chat_id] = count
        if count == 4 and not warning_sent.get(chat_id, False):
            await event.reply("⚠️ Don't spam!")
            warning_sent[chat_id] = True

        # Auto-reply cooldown
        if chat_id not in last_reply_time or now_time - last_reply_time[chat_id] > LIMIT_SECONDS:
            reply_text = get_current_reply()
            reply_msg = await event.reply(reply_text)
            replied_messages[chat_id] = reply_msg.id
            last_reply_time[chat_id] = now_time

# -----------------------------
async def auto_delete_loop():
    while True:
        await asyncio.sleep(60)
        for chat_id, msg_id in list(replied_messages.items()):
            try:
                await client.delete_messages(chat_id, msg_id, revoke=True)
                del replied_messages[chat_id]
            except:
                pass

# -----------------------------
async def main():
    await client.start(phone=phone)
    print("🤖 Ultimate Telegram Auto-Reply Bot running...")
    await asyncio.gather(client.run_until_disconnected(), auto_delete_loop())

# -----------------------------
with client:
    client.loop.run_until_complete(main())