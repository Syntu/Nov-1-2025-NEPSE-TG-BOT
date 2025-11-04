import os
import json
import logging
import requests
import asyncio
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
from dotenv import load_dotenv

# ---------- Logging ----------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---------- Load Environment Variables ----------
load_dotenv()
TOKEN = os.getenv("TELEGRAM_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://tg1nov.onrender.com/")
BOT_OWNER_CHAT_ID = int(os.getenv("BOT_OWNER_CHAT_ID", "0"))

# ---------- Flask App ----------
app = Flask(__name__)

# ---------- File persistence ----------
DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"users": {}, "subscribers": [], "active_users": []}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

data = load_data()

# ---------- Telegram App ----------
application = ApplicationBuilder().token(TOKEN).build()
bot = Bot(token=TOKEN)

# ---------- Web Scraping ----------
def _fetch_table_data(url, symbol, indices_map):
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
    except Exception as e:
        logger.error(f"Request failed: {e}")
        return None

    soup = BeautifulSoup(res.text, "html.parser")
    table = soup.find("table", class_="dataTable")
    if not table:
        return None

    rows = table.find("tbody").find_all("tr")
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < max(indices_map.values()) + 1:
            continue
        if cols[1].text.strip().upper() == symbol.upper():
            d = {}
            for k, i in indices_map.items():
                val = cols[i].text.strip().replace(",", "")
                try:
                    d[k] = float(val) if k not in ["Change Percent", "Volume"] else val
                except:
                    d[k] = val
            return d
    return None

def fetch_stock_data(symbol):
    live_map = {'LTP': 2, 'Change Percent': 4, 'Day High': 6, 'Day Low': 7, 'Volume': 8, 'Previous Close': 9}
    week_map = {'52 Week High': 22, '52 Week Low': 23}

    live = _fetch_table_data("https://www.sharesansar.com/live-trading", symbol, live_map)
    week = _fetch_table_data("https://www.sharesansar.com/today-share-price", symbol, week_map)
    if not live or not week:
        return None

    ltp, high, low = live["LTP"], week["52 Week High"], week["52 Week Low"]
    live.update(week)
    live.update({
        "Down From High": round(((high - ltp) / high) * 100, 2),
        "Up From Low": round(((ltp - low) / low) * 100, 2),
    })
    return live

def fetch_nepse_index_data():
    try:
        res = requests.get("https://www.sharesansar.com/live-trading", timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        box = soup.find("div", class_="index-summary-box")
        if not box:
            return None
        index_value = float(box.find("h4").text.strip().replace(",", ""))
        change_el = box.find("span", class_="text-danger") or box.find("span", class_="text-success")
        change = change_el.text.strip() if change_el else "N/A"
        return {"Index": index_value, "Change": change}
    except Exception as e:
        logger.error(e)
        return None

# ---------- Handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if str(chat_id) not in data["users"]:
        data["users"][str(chat_id)] = {"full_name": user.full_name, "username": user.username}
        save_data(data)
    if chat_id not in data["active_users"]:
        data["active_users"].append(chat_id)
        save_data(data)
    msg = (
        "नमस्ते 🙏 Syntoo's Nepse Bot मा स्वागत छ!\n\n"
        "के को डाटा चाहियो? Symbol पठाउनुहोस् (उदाहरण: SHINE, NABIL, SCB)\n\n"
        "दैनिक बजार सारांशको लागि /subscribe लेख्नुहोस्।"
    )
    await update.message.reply_text(msg)

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in data["subscribers"]:
        data["subscribers"].append(chat_id)
        save_data(data)
    await update.message.reply_text("✅ दैनिक बजार सारांश सदस्यता सफल।\n/unsubscribe गरेर रद्द गर्न सक्नुहुन्छ।")

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in data["subscribers"]:
        data["subscribers"].remove(chat_id)
        save_data(data)
        await update.message.reply_text("❌ सदस्यता रद्द भयो।")
    else:
        await update.message.reply_text("पहिले सदस्यता लिएको छैन।")

async def handle_stock_symbol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().upper()
    if not text.isalnum() or len(text) > 10:
        await update.message.reply_text("कृपया मान्य Symbol पठाउनुहोस् (जस्तै: SHINE)")
        return
    data_stock = fetch_stock_data(text)
    if not data_stock:
        await update.message.reply_text(f"{text} को डाटा भेटिएन।")
        return
    msg = (
        f"📊 <b>{text}</b> स्टक डाटा:\n\n"
        f"💰 LTP: {data_stock['LTP']}\n"
        f"🔄 Change: {data_stock['Change Percent']}\n"
        f"🔼 High: {data_stock['Day High']} | 🔽 Low: {data_stock['Day Low']}\n"
        f"52W High: {data_stock['52 Week High']} | 52W Low: {data_stock['52 Week Low']}\n"
        f"🔻 High बाट कमी: {data_stock['Down From High']}%\n"
        f"🔺 Low बाट वृद्धि: {data_stock['Up From Low']}%\n\n"
        "धन्यवाद 🙏"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

async def send_daily_summary():
    nepse = fetch_nepse_index_data()
    if not nepse:
        return "Error fetching data"
    message = (
        f"📅 दैनिक NEPSE सारांश\n\n"
        f"NEPSE Index: {nepse['Index']}\n"
        f"Change: {nepse['Change']}\n\n"
        "थप डाटा हेर्न Symbol पठाउनुहोस्।"
    )
    success = 0
    for chat_id in data["subscribers"]:
        try:
            await bot.send_message(chat_id=chat_id, text=message)
            success += 1
        except Exception as e:
            logger.error(e)
    return f"Sent to {success} users"

# ---------- Command setup ----------
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("subscribe", subscribe))
application.add_handler(CommandHandler("unsubscribe", unsubscribe))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_stock_symbol))

# ---------- Flask Routes ----------
@app.route("/")
def home():
    return "✅ Syntoo Nepse Bot is Live on Render!", 200

@app.route("/" + TOKEN, methods=["POST"])
def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), bot)
        asyncio.get_event_loop().create_task(application.process_update(update))
        return jsonify({"ok": True})
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/send_daily_summary")
def send_summary_route():
    msg = asyncio.get_event_loop().run_until_complete(send_daily_summary())
    return jsonify({"status": msg})

# ---------- Run ----------
if __name__ == "__main__":
    async def setup():
        full_url = f"{WEBHOOK_URL}{TOKEN}"
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_webhook(full_url)
        logger.info(f"✅ Webhook set to {full_url}")

    asyncio.get_event_loop().run_until_complete(setup())

    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
