import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
from dotenv import load_dotenv
from flask import Flask
import logging
from threading import Thread

# Load environment variables
load_dotenv()

# Flask app
app = Flask(__name__)

# Function to fetch stock data
def fetch_stock_data_by_symbol(symbol):
    url = "https://nepse.ct.ws/"
    response = requests.get(url)
    
    if response.status_code != 200:
        print("Error: Unable to fetch data from Sharesansar. Status code:", response.status_code)
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table')
    if not table:
        print("Error: No table found in the response.")
        return None
    
    rows = table.find_all('tr')[1:]

    for row in rows:
        cols = row.find_all('td')
        row_symbol = cols[1].text.strip()

        if row_symbol.upper() == symbol.upper():
            LTP = cols[2].text.strip()
            change_percent = cols[3].text.strip()
            day_high = cols[4].text.strip()
            day_low = cols[5].text.strip()
            previous_close = cols[6].text.strip()
            volume = cols[7].text.strip()
            turnover = cols[8].text.strip()
            week_52_high = cols[9].text.strip()
            week_52_low = cols[10].text.strip()
            down_from_high = cols[11].text.strip()
            up_from_low = cols[12].text.strip()

            return {
                'Symbol': symbol,
                'LTP': LTP,
                'Change Percent': change_percent,
                'Day High': day_high,
                'Day Low': day_low,
                'Previous Close': previous_close,
                'Volume': volume,
                'Turnover': turnover,
                '52 Week High': week_52_high,
                '52 Week Low': week_52_low,
                'Down from High': down_from_high,
                'Up from Low': up_from_low
            }
    return None

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "Welcome to Syntu's NEPSE BOT\n"
        "कृपया स्टकको सिम्बोल दिनुहोस्।\n"
        "उदाहरण: SHINE, SCB, SWBBL, SHPC"
    )
    await update.message.reply_text(welcome_message)

# Default handler for stock symbol
async def handle_stock_symbol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.strip().upper()
    data = fetch_stock_data_by_symbol(symbol)

    if data:
        response = (
            f"Stock Data for <b>{data['Symbol']}</b>:\n\n"
            f"LTP: {data['LTP']}\n"
            f"Change Percent: {data['Change Percent']}\n"
            f"Day High: {data['Day High']}\n"
            f"Day Low: {data['Day Low']}\n"
            f"Previous Close: {data['Previous Close']}\n"
            f"Volume: {data['Volume']}\n"
            f"Turnover: {data['Turnover']}\n"
            f"52 Week High: {data['52 Week High']}\n"
            f"52 Week Low: {data['52 Week Low']}\n"
            f"Down from High: {data['Down from High']}\n"
            f"Up from Low: {data['Up from Low']}"
        )
    else:
        response = f"""Symbol '{symbol}' फेला परेन 🤗🤗।
        कि Symbol को Spelling मिलेन ? अझै Try गर्नुस।"""
    await update.message.reply_text(response, parse_mode=ParseMode.HTML)

# Start the Flask server to make the app available for webhook
@app.route('/')
def index():
    return "Telegram bot is running!"

# Main function to set up the bot and run polling
if __name__ == "__main__":
    # Fetch the port assigned by Render (make sure your app binds to this port)
    port = int(os.getenv("PORT", 5000))  # Default to 5000 if PORT is not set

    # Telegram bot application
    TOKEN = os.getenv("TELEGRAM_API_KEY")
    application = ApplicationBuilder().token(TOKEN).build()

    # Add handlers to the application
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_stock_symbol))

    # Run Telegram bot and Flask server
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

    # Flask app runs on the port specified by Render
    thread = Thread(target=app.run, kwargs={"host": "0.0.0.0", "port": port})
    thread.start()

    # Run the Telegram bot polling
    application.run_polling()
