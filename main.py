import os
from flask import Flask
import logging, os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN = "8629762808:AAH-HZAl01nXCB7Psm2uRPrtawgpXFmVrfA"
ADMIN_ID = 8714423440
UPI_ID = "kingservice@naviaxis"

SERVICES = {
    "insta_50k": {"name": "Instagram Follower 50K", "price": "₹120"},
    "insta_100k": {"name": "Instagram Follower 100K", "price": "₹210"},
    "insta_blue": {"name": "Instagram Blue Tick", "price": "₹330"},
    "tg_prem_3m": {"name": "Telegram Premium 3 Month", "price": "₹140"},
    "tg_prem_1y": {"name": "Telegram Premium 1 Year", "price": "₹350"},
    "tg_star": {"name": "Telegram 100 Star", "price": "₹120"},
    "tg_member": {"name": "Telegram Member 50K", "price": "₹160"},
    "yt_sub": {"name": "YouTube Subscriber 50K", "price": "₹300"},
    "yt_monet": {"name": "YouTube Monetization", "price": "₹250"},
    "netflix": {"name": "Netflix OTT - 1 Saal", "price": "₹120"},
    "prime": {"name": "Prime Video OTT - 1 Saal", "price": "₹120"},
    "hotstar": {"name": "Hotstar OTT - 1 Saal", "price": "₹120"},
    "amazon_gc": {"name": "Amazon Gift Card - 500 Balance", "price": "₹100"},
    "play_gc": {"name": "Play Store Gift Card - 500 Balance", "price": "₹100"},
    "google_gc": {"name": "Google Play Gift Card - 500 Balance", "price": "₹100"},
    "bms_gc": {"name": "BookMyShow Gift Card - 500 Balance", "price": "₹100"},
}

help_data = {}
payment_data = {}
user_state = {}
next_id = [1]
logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎬 OTT Plans - Netflix / Prime / Hotstar", callback_data="cat_ott")],
        [InlineKeyboardButton("📸 Instagram Services", callback_data="cat_insta")],
        [InlineKeyboardButton("✈️ Telegram Services", callback_data="cat_tg")],
        [InlineKeyboardButton("▶️ YouTube Services", callback_data="cat_yt")],
        [InlineKeyboardButton("🎁 Gift Cards", callback_data="cat_gc")],
        [InlineKeyboardButton("🆘 HELP - Problem Likho", callback_data="help")],
        [InlineKeyboardButton("💳 PAYMENT - QR + UTR", callback_data="payment")],
    ]
    await update.message.reply_text("👑 *KING SERVICE*\nBest Price • Fast Delivery • Trusted\n\nCategory select karo:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    data = q.data
    cats = {
        "cat_ott": ["netflix", "prime", "hotstar"],
        "cat_insta": ["insta_50k", "insta_100k", "insta_blue"],
        "cat_tg": ["tg_prem_3m", "tg_prem_1y", "tg_star", "tg_member"],
        "cat_yt": ["yt_sub", "yt_monet"],
        "cat_gc": ["amazon_gc", "play_gc", "google_gc", "bms_gc"],
    }
    if data in cats:
        kb = []
        for key in cats[data]:
            s = SERVICES[key]
            kb.append([InlineKeyboardButton(f"{s['name']} - {s['price']}", callback_data=f"service_{key}")])
        kb.append([InlineKeyboardButton("⬅️ Back", callback_data="back")])
        await q.message.reply_text("Select karo:", reply_markup=InlineKeyboardMarkup(kb))
        return
    if data == "back":
        await start(q, context); return
    if data.startswith("service_"):
        key = data.replace("service_", "")
        s = SERVICES[key]
        await q.message.reply_text(f"👑 *{s['name']}*\n\nPrice: *{s['price']}*\n\nOrder ke liye *PAYMENT* dabao.", parse_mode="Markdown")
        return
    if data == "help":
        user_state[uid] = "waiting_help"
        await q.message.reply_text("🆘 *Apni problem likho:*", parse_mode="Markdown")
    elif data == "payment":
        user_state[uid] = "waiting_utr"
        if os.path.exists("qr.jpg"):
            with open("qr.jpg", "rb") as f:
                await q.message.reply_photo(photo=f, caption=f"💳 *PAYMENT KARO*\n\nUPI ID: `{UPI_ID}`\n\n1. Is QR ko Scan karo ya UPI ID copy karo\n2. Payment karo\n3. Uske baad *UTR Number yahan bhejo*", parse_mode="Markdown")
        else:
            await q.message.reply_text(f"💳 *PAYMENT KARO*\n\nUPI ID: `{UPI_ID}`\n\nPayment karke *UTR Number bhejo:*", parse_mode="Markdown")

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    uname = update.message.from_user.username or update.message.from_user.first_name
    text = update.message.text or ""
    state = user_state.get(uid)
    if text.startswith("/reply"):
        if uid != ADMIN_ID:
            await update.message.reply_text("Tu Admin nahi hai!"); return
        try:
            parts = text.split(" ", 2)
            target_id = int(parts[1]); msg = parts[2]
            target_uid = None
            for d in list(help_data.values()) + list(payment_data.values()):
                if d['id'] == target_id:
                    target_uid = d['uid']; break
            if target_uid:
                await context.bot.send_message(chat_id=target_uid, text=f"👑 *KING SERVICE se Reply:*\n\n{msg}", parse_mode="Markdown")
                await update.message.reply_text("✅ Reply bhej diya!")
            else:
                await update.message.reply_text("ID nahi mili!")
        except:
            await update.message.reply_text("Aise likho: /reply 1 Haan ho gaya")
        return
    if text.startswith("/admin"):
        if uid != ADMIN_ID:
            await update.message.reply_text("Sirf Admin dekh sakta hai!"); return
        msg = "👑 *ADMIN PANEL*\n\n"
        if not help_data and not payment_data:
            msg += "Abhi kuch nahi hai."
        for d in help_data.values():
            msg += f"\n#{d['id']} @{d['user']} | HELP | {d['text']}"
        for d in payment_data.values():
            msg += f"\n#{d['id']} @{d['user']} | PAYMENT | UTR: {d['utr']}"
        msg += "\n\nDelete: /delete 1\nReply: /reply 1 Hii\nClear: /clear"
        await update.message.reply_text(msg, parse_mode="Markdown")
        return
    if text.startswith("/delete"):
        if uid != ADMIN_ID: return
        try:
            del_id = int(text.split()[1])
            help_data.pop(del_id, None); payment_data.pop(del_id, None)
            await update.message.reply_text(f"✅ #{del_id} delete ho gaya!")
        except:
            await update.message.reply_text("Aise likho: /delete 1")
        return
    if text.startswith("/clear"):
        if uid != ADMIN_ID: return
        help_data.clear(); payment_data.clear()
        await update.message.reply_text("✅ Sab clear ho gaya!")
        return
    if state == "waiting_help":
        nid = next_id[0]; next_id[0] += 1
        help_data[nid] = {'id': nid, 'uid': uid, 'user': uname, 'text': text}
        user_state.pop(uid, None)
        await update.message.reply_text("✅ Problem Admin ko bhej di gayi hai.")
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"🔔 *Nayi HELP* #{nid}\nUser: @{uname}\nProblem: {text}", parse_mode="Markdown")
    elif state == "waiting_utr":
        context.user_data['utr'] = text
        user_state[uid] = "waiting_screenshot"
        await update.message.reply_text("✅ UTR mil gaya!\n\nAb *Payment ka Screenshot bhejo:*", parse_mode="Markdown")
    elif state == "waiting_screenshot":
        if update.message.photo:
            nid = next_id[0]; next_id[0] += 1
            payment_data[nid] = {'id': nid, 'uid': uid, 'user': uname, 'utr': context.user_data.get('utr')}
            user_state.pop(uid, None)
            await update.message.reply_text("✅ Payment Admin ko bhej diya hai. Admin check karke reply karega.")
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"🔔 *Naya PAYMENT* #{nid}\nUser: @{uname}\nUTR: {context.user_data.get('utr')}", parse_mode="Markdown")
            await context.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, caption=f"Payment Screenshot - #{nid} @{uname}")
        else:
            await update.message.reply_text("Screenshot bhejo, photo bhejo.")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_msg))
    print("Bot Chal Gaya...")
    await app.run_polling()
import asyncio
asyncio.run(main())
# Render ko zinda rakhne ke liye
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is Running"
import threading
threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))).start()
