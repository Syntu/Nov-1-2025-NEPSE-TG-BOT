import os
import requests
from bs4 import BeautifulSoup
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from dotenv import load_dotenv
from flask import Flask, request

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
PORT = int(os.getenv('PORT', 5000))  # Default to port 5000 if PORT is not set
bot = Bot(token=TOKEN)

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        update = Update.de_json(request.get_json(), bot)
        application.process_update(update)
        return "ok", 200

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Welcome 🙏 to Syntoo's NEPSE💹bot!\n"
        "के को डाटा चाहियो भन्नुस ?\n"
        "म फ्याट्टै खोजिहाल्छु 😂😅\n"
        "Symbol दिनुस जस्तै:- NMB, SHINE, SHPC, SWBBL"
    )

async def fetch_stock_data(symbol):
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

async def stock(update: Update, context: CallbackContext) -> None:
    symbol = update.message.text.upper()
    data = await fetch_stock_data(symbol)
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

application = Application.builder().token(TOKEN).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, stock))

if __name__ == '__main__':
    application.run_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
    application.bot.set_webhook(f"https://onesyntootg.onrender.com/{TOKEN}")

    app.run(host='0.0.0.0', port=PORT, debug=True)  # Ensure Flask app runs on the correct port