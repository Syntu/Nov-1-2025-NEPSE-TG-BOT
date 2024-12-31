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
    data = await fetch_stock_data(symbol)
    if data:
        response = (
            f"Latest stock Data for <b>{data['Symbol']}</b>:\n\n"
            f"LTP: {data['LTP']}\n"
            f"Change Percent: {data['Change Percent']}\n"
            f"Day High: {data['Day High']}\n"
            f"Day Low: {data['Day Low']}\n"
            f"52 Week High: {data['52 Week High']}\n"
            f"52 Week Low: {data['52 Week Low']}\n"
            f"Volume: {data['Volume']}\n"
            f"Turnover: {data['Turnover']}\n"
            f"Down from High: {data['Down from High']}\n"
            f"Up from Low: {data['Up from Low']}"
        )
        await update.message.reply_text(response, parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(f"Stock symbol {symbol} not found.")

async def main():
    application = ApplicationBuilder().token(TELEGRAM_BOT_API).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stock", stock))

    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())