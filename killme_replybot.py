# replybot.py
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

# Dummy HTTP health check server
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is alive!')

def run_http_server():
    server = HTTPServer(("", 8080), HealthHandler)
    server.serve_forever()

threading.Thread(target=run_http_server, daemon=True).start()

# Bot setup
TOKEN = os.getenv("BOT_TOKEN")
EXCLUDED_IDS = [-1001984521739, -1002136991674, 5764304134]

# Dictionary to track user messages
user_messages = {}

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello Watcher! I am alive and running!")

# /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 *Bot Commands:*\n"
        "/start – Start the bot\n"
        "/help – Show this help menu\n\n"
        "📬 *Need Help?* [𝐇𝐞𝐥𝐩 𝐨𝐫 𝐑𝐞𝐩𝐨𝐫𝐭 𝐛𝐨𝐭](http://t.me/Fedbk_rep_bot)",
        parse_mode="Markdown"
    )

# Main reply logic
async def reply_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    message_text = update.message.text.strip()

    if chat.type in ["group", "supergroup"]:
        if update.message.sender_chat and update.message.sender_chat.id in EXCLUDED_IDS:
            return
        if user and user.id in EXCLUDED_IDS:
            return

    uid = user.id
    current = user_messages.get(uid)

    if current and current["text"] == message_text:
        try:
            await context.bot.delete_message(chat_id=chat.id, message_id=current["bot_msg_id"])
        except:
            pass
        sent = await update.message.reply_text(
            "ᴀʟʀᴇᴀᴅʏ ɴᴏᴛᴇᴅ ✅\nᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ⏳..."
        )
        user_messages[uid] = {"text": message_text, "bot_msg_id": sent.message_id}
    else:
        sent = await update.message.reply_text(
            "ʀᴇQᴜᴇꜱᴛ ʀᴇᴄᴇɪᴠᴇᴅ✅\nᴜᴘʟᴏᴀᴅ ꜱᴏᴏɴ... ᴄʜɪʟʟ✨"
        )
        user_messages[uid] = {"text": message_text, "bot_msg_id": sent.message_id}

# Build app
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_message))
app.run_polling()
