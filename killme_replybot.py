# killme_replybot.py
# Telegram bot that cleans mentions/domains in channels and replies in groups
# Fully DB-driven: add/remove allowed channels/groups/excluded IDs

import asyncio
import re
from pyrogram import Client, filters
from pyrogram.types import Message
from motor.motor_asyncio import AsyncIOMotorClient
from config import API_ID, API_HASH, BOT_TOKEN, MONGO_URL, OWNER_ID

app = Client("killme_replybot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
db = AsyncIOMotorClient(MONGO_URL).killme_bot

# ------------------------ DB HELPERS ------------------------ #

async def is_allowed_channel(chat_id):
    doc = await db.channels.find_one({"_id": chat_id})
    return bool(doc)

async def is_allowed_group(chat_id):
    doc = await db.groups.find_one({"_id": chat_id})
    return bool(doc)

async def is_excluded(user_id):
    doc = await db.excluded.find_one({"_id": user_id})
    return bool(doc)

# ------------------------ CLEANER ------------------------ #

def clean_message(text):
    if not text:
        return text
    # Remove mentions, t.me links, and domains
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"https?://t\.me/\S+", "", text)
    text = re.sub(r"\b\w+\.(com|org|in|me|net|live|app|shop|info|link|xyz|lol|tube)\b", "", text, flags=re.IGNORECASE)
    return text.strip()

# ------------------------ HANDLERS ------------------------ #

@app.on_message(filters.channel)
async def channel_cleaner(client, msg: Message):
    if not await is_allowed_channel(msg.chat.id):
        return
    if not (msg.text or msg.caption):
        return

    text = msg.text or msg.caption
    cleaned = clean_message(text)

    if msg.media:
        await msg.copy(msg.chat.id, caption=cleaned)
    else:
        await msg.reply(cleaned)

@app.on_message(filters.group & filters.incoming)
async def group_reply(client, msg: Message):
    if not await is_allowed_group(msg.chat.id):
        return

    user_id = msg.from_user.id if msg.from_user else None
    sender_id = msg.sender_chat.id if msg.sender_chat else None

    if await is_excluded(msg.chat.id) or await is_excluded(user_id) or await is_excluded(sender_id):
        return

    if msg.text:
        await msg.reply("Hello! Your message has been received ✨")

# ------------------------ ADMIN COMMANDS ------------------------ #

@app.on_message(filters.private & filters.user(OWNER_ID) & filters.command("add_chnl"))
async def add_channel(_, msg):
    if len(msg.command) < 2:
        return await msg.reply("Send channel ID like: /add_chnl -100xxxx")
    chat_id = int(msg.command[1])
    await db.channels.update_one({"_id": chat_id}, {"$set": {"_id": chat_id}}, upsert=True)
    await msg.reply(f"✅ Added channel `{chat_id}`")

@app.on_message(filters.private & filters.user(OWNER_ID) & filters.command("add_grp"))
async def add_group(_, msg):
    if len(msg.command) < 2:
        return await msg.reply("Send group ID like: /add_grp -100xxxx")
    chat_id = int(msg.command[1])
    await db.groups.update_one({"_id": chat_id}, {"$set": {"_id": chat_id}}, upsert=True)
    await msg.reply(f"✅ Added group `{chat_id}`")

@app.on_message(filters.private & filters.user(OWNER_ID) & filters.command("add_exclude"))
async def add_exclude(_, msg):
    if len(msg.command) < 2:
        return await msg.reply("Send user/chat ID to exclude")
    uid = int(msg.command[1])
    await db.excluded.update_one({"_id": uid}, {"$set": {"_id": uid}}, upsert=True)
    await msg.reply(f"✅ Excluded ID `{uid}`")

@app.on_message(filters.private & filters.user(OWNER_ID) & filters.command("del_chnl"))
async def del_channel(_, msg):
    if len(msg.command) < 2:
        return await msg.reply("Send channel ID to remove")
    cid = int(msg.command[1])
    await db.channels.delete_one({"_id": cid})
    await msg.reply(f"❌ Removed channel `{cid}`")

@app.on_message(filters.private & filters.user(OWNER_ID) & filters.command("del_grp"))
async def del_group(_, msg):
    if len(msg.command) < 2:
        return await msg.reply("Send group ID to remove")
    gid = int(msg.command[1])
    await db.groups.delete_one({"_id": gid})
    await msg.reply(f"❌ Removed group `{gid}`")

@app.on_message(filters.private & filters.user(OWNER_ID) & filters.command("list_chnl"))
async def list_channels(_, msg):
    chs = await db.channels.find().to_list(None)
    if not chs:
        return await msg.reply("No channels added.")
    txt = "**Allowed Channels:**\n" + "\n".join([f"`{c['_id']}`" for c in chs])
    await msg.reply(txt)

@app.on_message(filters.private & filters.user(OWNER_ID) & filters.command("list_grp"))
async def list_groups(_, msg):
    grs = await db.groups.find().to_list(None)
    if not grs:
        return await msg.reply("No groups added.")
    txt = "**Allowed Groups:**\n" + "\n".join([f"`{g['_id']}`" for g in grs])
    await msg.reply(txt)

# ------------------------ ALIVE LOOP ------------------------ #

async def keep_alive():
    while True:
        await asyncio.sleep(3600)

# ------------------------ START BOT ------------------------ #

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(keep_alive())
    app.run()
