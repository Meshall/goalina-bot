import os, json, requests, threading
from websocket import create_connection
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram import Update

# ===== CONFIG (loaded from Railway env vars) =====
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
BTC_ADDRESS = os.getenv("BTC_ADDRESS")
GOAL_BTC = float(os.getenv("GOAL_BTC", "1.0"))
# =================================================

progress_message_id = None

def get_balance_btc(address: str) -> float:
    url = f"https://blockstream.info/api/address/{address}"
    r = requests.get(url).json()
    funded = r["chain_stats"]["funded_txo_sum"]
    spent = r["chain_stats"]["spent_txo_sum"]
    return (funded - spent) / 1e8

def format_progress(balance: float) -> str:
    return (
        f"🎯 Goal: {GOAL_BTC:.8f} BTC\n"
        f"💰 Current Balance: {balance:.8f} BTC\n"
        f"📈 Progress: {(balance/GOAL_BTC)*100:.2f}%"
    )

def ensure_progress_message(context: CallbackContext):
    global progress_message_id
    balance = get_balance_btc(BTC_ADDRESS)
    msg = format_progress(balance)
    if progress_message_id is None:
        sent = context.bot.send_message(chat_id=CHAT_ID, text=msg)
        progress_message_id = sent.message_id
    else:
        context.bot.edit_message_text(chat_id=CHAT_ID, message_id=progress_message_id, text=msg)

def progress(update: Update, context: CallbackContext):
    ensure_progress_message(context)
    update.message.reply_text("Progress refreshed ✅")

def websocket_listener(bot):
    ws = create_connection("wss://blockstream.info/api/ws")
    ws.send(json.dumps({"op": "addr_sub", "addr": BTC_ADDRESS}))
    while True:
        try:
            data = json.loads(ws.recv())
            if data.get("op") == "utx":
                balance = get_balance_btc(BTC_ADDRESS)
                msg = format_progress(balance)
                if progress_message_id:
                    bot.edit_message_text(chat_id=CHAT_ID, message_id=progress_message_id, text=msg)
        except Exception as e:
            print("⚠️ WebSocket error:", e)
            ws.close()
            ws = create_connection("wss://blockstream.info/api/ws")
            ws.send(json.dumps({"op": "addr_sub", "addr": BTC_ADDRESS}))

def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("progress", progress))
    threading.Thread(target=websocket_listener, args=(updater.bot,), daemon=True).start()
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
