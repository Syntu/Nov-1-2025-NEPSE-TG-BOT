import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext
from telegram.ext import filters  # Correct import for filters
import requests
from bs4 import BeautifulSoup

# Load environment variables from the .env file
load_dotenv()

# Load the Telegram Bot API token and port from environment variables
BOT_TOKEN = os.getenv("TELEGRAM_BOT_API")
PORT = int(os.getenv("PORT"))

# Check if the BOT_TOKEN is loaded correctly
if not BOT_TOKEN:
    raise ValueError("Error: TELEGRAM_BOT_API token not found in environment variables.")

# Function to fetch stock data from NEPSE website
def fetch_stock_data(symbol: str):
    url = f"https://nepse.ct.ws/{symbol}"  # Update URL structure as needed
    response = requests.get(url)
    
    if response.status_code != 200:
        return {"Error": f"Failed to fetch data. HTTP Status Code: {response.status_code}"}
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    try:
        data = {
            "Symbol": symbol,
            "LTP": soup.find("span", {"class": "ltp"}).text.strip(),
            "Change Percent": soup.find("span", {"class": "change-percent"}).text.strip(),
            "Day High": soup.find("span", {"class": "day-high"}).text.strip(),
            "Day Low": soup.find("span", {"class": "day-low"}).text.strip(),
            "52 Week High": soup.find("span", {"class": "week-high"}).text.strip(),
            "52 Week Low": soup.find("span", {"class": "week-low"}).text.strip(),
            "Volume": soup.find("span", {"class": "volume"}).text.strip(),
            "Turnover": soup.find("span", {"class": "turnover"}).text.strip(),
            "Down from High": soup.find("span", {"class": "down-from-high"}).text.strip(),
            "Up from Low": soup.find("span", {"class": "up-from-low"}).text.strip(),
        }
        return data
    except AttributeError as e:
        return {"Error": f"Data extraction error: {str(e)}"}

# Handler for the /start command
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello! Send a stock symbol to get data.")

# Handler for messages that fetch stock data based on the symbol
def handle_message(update: Update, context: CallbackContext):
    text = update.message.text.strip()
    
    if text.isupper() and len(text) <= 5:  # Symbol validation (1-5 characters, uppercase)
        stock_data = fetch_stock_data(text)
        
        if "Error" in stock_data:
            update.message.reply_text(f"Error: {stock_data['Error']}")
        else:
            response = (
                f"Latest stock data for <b>{stock_data['Symbol']}</b>:\n\n"
                f"LTP: {stock_data['LTP']}\n"
                f"Change Percent: {stock_data['Change Percent']}\n"
                f"Day High: {stock_data['Day High']}\n"
                f"Day Low: {stock_data['Day Low']}\n"
                f"52 Week High: {stock_data['52 Week High']}\n"
                f"52 Week Low: {stock_data['52 Week Low']}\n"
                f"Volume: {stock_data['Volume']}\n"
                f"Turnover: {stock_data['Turnover']}\n"
                f"Down from High: {stock_data['Down from High']}\n"
                f"Up from Low: {stock_data['Up from Low']}"
            )
            update.message.reply_text(response, parse_mode='HTML')
    else:
        update.message.reply_text("Please send a valid stock symbol (e.g., ABC).")

# Main function to set up the bot
def main():
    # Set up the Updater and Dispatcher
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    # Command handler for /start
    dispatcher.add_handler(CommandHandler('start', start))

    # Message handler for stock symbol messages
    dispatcher.add_handler(MessageHandler(filters.Text & ~filters.Command, handle_message))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
