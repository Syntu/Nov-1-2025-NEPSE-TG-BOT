import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from telegram import Update, ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Load environment variables from .env file
load_dotenv()

TELEGRAM_BOT_API = os.getenv('TELEGRAM_BOT_API')
PORT = int(os.getenv('PORT', '5000'))

async def fetch_stock_data(symbol):
    url = f"https://nepse.ct.ws/api/stock/{symbol}"  # Replace with the actual endpoint
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to the Stock Bot! Use /stock <symbol> to get the latest stock data.")

async def stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Please provide a stock symbol. Usage: /stock <symbol>")
        return

    symbol = context.args[0].upper()
    data = await fetch_stock_data(symbol)import os
import requests
from bs4 import BeautifulSoup
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from dotenv import load_dotenv
from flask import Flask, request

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=TOKEN)

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        update = Update.de_json(request.get_json(), bot)
        dp.process_update(update)
        return "ok", 200

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Welcome 🙏 to Syntoo's NEPSE💹bot!\n"
        "के को डाटा चाहियो भन्नुस ?\n"
        "म फ्याट्टै खोजिहाल्छु 😂😅\n"
        "Symbol दिनुस जस्तै:- NMB, SHINE, SHPC, SWBBL"
    )

def get_stock_data(symbol):
    url = f"https://nepse.ct.ws/{symbol}"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract the required data from the soup object
        data = {
            "Symbol": symbol,
            "LTP": soup.find('span', {'id': 'last_price'}).text,
            "Change Percent": soup.find('span', {'id': 'change_percent'}).text,
            "Day High": soup.find('span', {'id': 'day_high'}).text,
            "Day Low": soup.find('span', {'id': 'day_low'}).text,
            "Volume": soup.find('span', {'id': 'volume'}).text,
            "Turn Over": soup.find('span', {'id': 'turn_over'}).text,
            "52 Week High": soup.find('span', {'id': '52_week_high'}).text,
            "52 Week Low": soup.find('span', {'id': '52_week_low'}).text,
            "Down From High%": soup.find('span', {'id': 'down_from_high'}).text,
            "Up From Low%": soup.find('span', {'id': 'up_from_low'}).text,
        }
        return data
    else:
        return None

def stock(update: Update, context: CallbackContext) -> None:
    symbol = update.message.text.upper()
    data = get_stock_data(symbol)
    if data:
        response = (
            f"Symbol: {data['Symbol']}\n"
            f"LTP: {data['LTP']}\n"
            f"Change Percent: {data['Change Percent']}\n"
            f"Day High: {data['Day High']}\n"
            f"Day Low: {data['Day Low']}\n"
            f"Volume: {data['Volume']}\n"
            f"Turn Over: {data['Turn Over']}\n"
            f"52 Week High: {data['52 Week High']}\n"
            f"52 Week Low: {data['52 Week Low']}\n"
            f"Down From High%: {data['Down From High%']}\n"
            f"Up From Low%: {data['Up From Low%']}"
        )
    else:
        response = (
            f"Symbol ..... 'ल्या, फेला परेन त 🤗🤗।\n"
            f"नआत्तिनु Symbol राम्रो सङ्ग फेरि दिनुस।\n"
            f"म फेरि खोज्छु।"
        )
    update.message.reply_text(response)

updater = Updater(TOKEN)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, stock))

if __name__ == '__main__':
    updater.start_webhook(listen="0.0.0.0", port=int(os.getenv("PORT")), url_path=TOKEN)
    updater.bot.set_webhook(f"https://{your_domain}/{TOKEN}")

    app.run(port=int(os.getenv("PORT")), debug=True)