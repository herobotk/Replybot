# -------------------------------
# Health check server (top of file)
# -------------------------------
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is alive!')

def run_http_server():
    server = HTTPServer(("", 8080), HealthHandler)
    server.serve_forever()

# Start dummy HTTP server in background
threading.Thread(target=run_http_server, daemon=True).start()

# -------------------------------
# Your actual bot code (v20.6 compatible)
# -------------------------------
import os
from telegram import Update, ChatMember
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Get bot token from environment variable
TOKEN = os.getenv("BOT_TOKEN")

# IDs that are excluded from replies
EXCLUDED_IDS = [-1001984521739, -1002136991674, 5764304134]

# Track which users already sent a message
replied_users = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello Watcher! I am alive and running!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 *Bot Commands:*\n"
        "/start – Start the bot\n"
        "/help – Show this help menu\n\n"
        "📬 *Need Help?* [Click Here](http://t.me/Fedbk_rep_bot)",
        parse_mode="Markdown"
    )

async def reply_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    if not update.message or not user:
        return

    # Avoid replies to excluded IDs
    if chat.type in ["group", "supergroup"]:
        if update.message.sender_chat and update.message.sender_chat.id in EXCLUDED_IDS:
            return
        if user.id in EXCLUDED_IDS:
            return
        try:
            member: ChatMember = await context.bot.get_chat_member(chat.id, user.id)
            if member.status in ["administrator", "creator"]:
                return
        except:
            pass

    # Already replied to this user before
    if user.id in replied_users:
        try:
            await update.message.delete()
        except:
            pass
        await update.message.reply_text("✅ Your request has been recorded. Please wait while we process it... ⏳")
    else:
        replied_users.add(user.id)
        await update.message.reply_text("ʀᴇQᴜᴇꜱᴛ ʀᴇᴄᴇɪᴠᴇᴅ✅\nᴜᴘʟᴏᴀᴅ ꜱᴏᴏɴ... ᴄʜɪʟʟ✨")

# Build and run application
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_message))

app.run_polling()
