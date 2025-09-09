# GoaLina Bot 🎯

A Telegram bot that tracks a Bitcoin donation goal in real time.

## Features
- Shows goal progress in percentage
- Updates a pinned message in your channel/group
- Supports `/progress` command
- Reacts to incoming + outgoing transactions

## Setup
1. Create a Telegram bot with [@BotFather](https://t.me/BotFather).
2. Deploy this repo to [Railway.app](https://railway.app).
3. Add the following environment variables in Railway:

```
TELEGRAM_BOT_TOKEN = your_bot_token
CHAT_ID = -100xxxxxxxxxx
BTC_ADDRESS = your_btc_address
GOAL_BTC = 0.1
```

4. Start the bot:
```
python main.py
```

5. Add your bot to a channel/group as Admin.
6. Run `/progress` to create the first tracker message.
7. Pin that message → it will auto-update on every transaction.
