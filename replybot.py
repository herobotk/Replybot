import os
from telegram import Update, ChatMember
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
EXCLUDED_IDS = [-1001984521739, -1002136991674, 5764304134]

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

    await update.message.reply_text("ʀᴇQᴜᴇꜱᴛ ʀᴇᴄᴇɪᴠᴇᴅ✅\nᴜᴘʟᴏᴀᴅ ꜱᴏᴏɴ... ᴄʜɪʟʟ✨")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_message))

app.run_polling()
