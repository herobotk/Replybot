import os
import re
import asyncio
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from humanize import naturalsize

# ============ CONFIG ============
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Channel and Group IDs
KILLME_CHANNELS = [-1002172427490, -1002027244866, -1002090397274]
REPLYBOT_GROUP = -1001984521739
GROUP_EXCLUDED_IDS = [-1001984521739, -1002136991674, 5764304134]

# Dictionary to track group replies
user_messages = {}

# ============ Health Check ============
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is alive!')

threading.Thread(target=lambda: HTTPServer(("", 8080), HealthHandler).serve_forever(), daemon=True).start()

# ============ Filename Cleaner ============
def clean_filename(filename: str) -> str:
    keep_username = "@movie_talk_backup"
    filename = filename.replace(keep_username, "___KEEP__USERNAME___")

    filename = re.sub(r'@\w+', '', filename)
    filename = re.sub(r'https?://\S+|www\.\S+|\S+\.(com|in|net|org|me|info)', '', filename)
    filename = re.sub(r't\.me/\S+', '', filename)
    filename = re.sub(r'[^\w\s.\-()_]', '', filename)
    filename = re.sub(r'\s{2,}', ' ', filename).strip()

    return filename.replace("___KEEP__USERNAME___", keep_username)

# ============ Caption Builder ============
def generate_caption(file_name, file_size):
    cleaned_name = clean_filename(file_name)
    return f"""{cleaned_name}
⚙️ 𝚂𝚒𝚣𝚎 ~ [{file_size}]
⚜️ 𝙿𝚘𝚜𝚝 𝚋𝚢 ~ 𝐌𝐎𝐕𝐈𝐄 𝐓𝐀𝐋𝐊

⚡𝖩𝗈𝗂𝗇 Us ~ ❤️ 
➦『 @movie_talk_backup 』"""

# ============ Bot Setup ============
bot = Client("killme_replybot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ============ Private Commands ============
@bot.on_message(filters.private & filters.command("start"))
async def start_cmd(_, message: Message):
    await message.reply("👋 Bot is alive! ReplyBot & KillMe logic activated.")

@bot.on_message(filters.private & filters.command("help"))
async def help_cmd(_, message: Message):
    await message.reply_text(
        "📌 Bot Commands:\n"
        "/start – Start\n"
        "/help – Help\n\n"
        "✅ Group: ReplyBot active\n"
        "✅ Channels: KillMe bot (mention/domain cleaner)",
        disable_web_page_preview=True
    )

# ============ Channel Handler (Kill Me Bot) ============
@bot.on_message(filters.channel & ~filters.me)
async def channel_handler(_, message: Message):
    if message.chat.id not in KILLME_CHANNELS:
        return

    media = message.document or message.video or message.audio
    original_caption = message.caption or ""

    if media and media.file_name:
        file_name = media.file_name
        file_size = naturalsize(media.file_size)
        caption = generate_caption(file_name, file_size)
    else:
        caption = clean_filename(original_caption)

    try:
        await message.copy(chat_id=message.chat.id, caption=caption)
        await message.delete()
    except FloodWait as e:
        await asyncio.sleep(e.value)
        try:
            await message.copy(chat_id=message.chat.id, caption=caption)
            await message.delete()
        except Exception as e2:
            print(f"[Retry Error] {e2}")
    except Exception as e:
        print(f"[Channel Error] {e}")

# ============ Group Handler (Reply Bot) ============
@bot.on_message(filters.group & filters.text & ~filters.command())
async def group_reply_handler(_, message: Message):
    if message.chat.id != REPLYBOT_GROUP:
        return

    if message.sender_chat and message.sender_chat.id in GROUP_EXCLUDED_IDS:
        return

    if message.from_user and message.from_user.id in GROUP_EXCLUDED_IDS:
        return

    user = message.from_user
    if not user:
        return

    uid = user.id
    text = message.text.strip()
    current = user_messages.get(uid)

    if current and current["text"] == text:
        try:
            await bot.delete_messages(message.chat.id, current["bot_msg_id"])
        except:
            pass
        sent = await message.reply_text("ᴀʟʀᴇᴀᴅʏ ɴᴏᴛᴇᴅ ✅\nᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ⏳...")
    else:
        sent = await message.reply_text("ʀᴇQᴜᴇꜱᴛ ʀᴇᴄᴇɪᴠᴇᴅ✅\nᴜᴘʟᴏᴀᴅ ꜱᴏᴏɴ... ᴄʜɪʟʟ✨")

    user_messages[uid] = {"text": text, "bot_msg_id": sent.id}

# ============ Run ============
bot.run()
