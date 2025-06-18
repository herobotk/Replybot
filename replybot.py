import os
print("Bot started!")
print("Doing something...")

from telegram import Update, ChatMember
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

# Telegram Bot Token from environment
TOKEN = os.environ.get("BOT_TOKEN")

# IDs to exclude (channels/admins/users)
EXCLUDED_IDS = [-1001984521739, -1002136991674, 5764304134]

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello Watcher! I am alive and running!")

# /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 *Bot Commands:*\n"
        "/start – Start the bot\n"
        "/help – Show this help menu\n\n"
        "📤 Send any message and I'll auto reply with a status update.\n\n"
        "📬 *Problem?* Contact: [𝐇𝐞𝐥𝐩 𝐨𝐫 𝐑𝐞𝐩𝐨𝐫𝐭 𝐛𝐨𝐭 ⚠️](http://t.me/Fedbk_rep_bot)",
        parse_mode="Markdown"
    )

# Auto reply message handler
async def reply_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    # Ignore specific users/channels/admins
    if chat.type in ["group", "supergroup"]:
        if update.message.sender_chat and update.message.sender_chat.id in EXCLUDED_IDS:
            return
        if user and user.id in EXCLUDED_IDS:
            return
        try:
            member: ChatMember = await context.bot.get_chat_member(chat.id, user.id)
            if member.status in ["administrator", "creator"]:
                return
        except:
            pass

    # Bot reply message
    await update.message.reply_text(
        "ʀᴇQᴜᴇꜱᴛ ʀᴇᴄᴇɪᴠᴇᴅ✅\n"
        "ᴜᴘʟᴏᴀᴅ ꜱᴏᴏɴ... ᴄʜɪʟʟ✨"
    )

# Application setup
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_message))

print("Bot is running...")
app.run_polling()
