# KillMe + ReplyBot Combo Bot 🤖🔥

A single Telegram bot that performs two separate roles:

- **KillMe Bot** (Channel): Automatically cleans mentions, links, and domains from captions or messages in specific channels, and re-uploads them with a clean caption.
- **ReplyBot** (Group): Smart auto-responder in group chats. Replies to repeated or unique messages based on user ID and avoids replying to specific users or channels.

---

## 🚀 Features

### 🔸 KillMe Bot (For Channels)
- Cleans mentions (like `@username`)
- Removes links (`t.me/`, `https://`, domains like `.com`, `.net`, etc.)
- Builds a clean caption with file size
- Reposts media with updated clean caption

### 🔸 Reply Bot (For Groups)
- Replies when a user sends a message
- If the same message is sent again, deletes the old reply and sends a new one
- Ignores messages from specific users/channels (like admins or bots)

---

## ⚙️ Configuration

Set these environment variables:

```env
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
