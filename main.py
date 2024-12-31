from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

# Function to fetch stock data
def fetch_stock_data_by_symbol(symbol):
    url = "https://nepse.ct.ws/"
    response = requests.get(url)

    if response.status_code != 200:
        print("Error: Unable to fetch data. Status code:", response.status_code)
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
            day_high = cols[4].text.strip()
            day_low = cols[5].text.strip()
            LTP = cols[2].text.strip()
            change_percent = cols[3].text.strip()
            volume = cols[7].text.strip()
            turnover = cols[8].text.strip()
            week_52_high = cols[9].text.strip()
            week_52_low = cols[10].text.strip()
            previous_close = cols[6].text.strip()
            down_from_high = cols[11].text.strip()
            up_from_low = cols[12].text.strip()

            return {
                'Symbol': symbol,
                'Day High': day_high,
                'Day Low': day_low,
                'LTP': LTP,
                'Change Percent': change_percent,
                'Volume': volume,
                'Turnover': turnover,
                '52 Week High': week_52_high,
                '52 Week Low': week_52_low,
                'Previous Close': previous_close,
                'Down from High': down_from_high,
                'Up from Low': up_from_low,
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
            f"Down from High: {data['Down from High']}\n"
            f"Up from Low: {data['Up from Low']}\n"
            f"52 Week High: {data['52 Week High']}\n"
            f"52 Week Low: {data['52 Week Low']}\n"
            f"Volume: {data['Volume']}\n"
            f"Turnover: {data['Turnover']}"
        )
    else:
        response = f"""Symbol '{symbol}' को डेटा फेला परेन।\nकृपया स्पेलिङ चेक गर्नुहोस् र पुन: प्रयास गर्नुहोस्।"""
    await update.message.reply_text(response, parse_mode=ParseMode.HTML)

# Main function to set up the bot and run polling
if __name__ == "__main__":
    TOKEN = os.getenv("TELEGRAM_API_KEY")

    # Set up Telegram bot application
    application = Application.builder().token(TOKEN).build()

    # Add handlers to the application
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_stock_symbol))

    # Start polling
    print("Starting polling...")
    application.run_polling()
