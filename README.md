
# Telegram Reply Bot 🤖

This is a simple Telegram bot that:
- Replies to user messages.
- Detects and handles duplicate messages.
- Sends a formal message if the same message is repeated.
- Deletes previous bot replies on repeat.

## 🚀 Setup

1. Clone this repo
2. Copy `.env.example` to `.env` and add your bot token
3. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the bot:
   ```bash
   python3 replybot.py
   ```

## 📦 Deploy to Koyeb

1. Push this to GitHub
2. Create new service in Koyeb from this repo
3. Set `BOT_TOKEN` in the environment variables section
4. Health check URL: `/`
5. Done! Your bot is live 🎉
