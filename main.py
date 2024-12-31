import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Function to fetch stock data
def fetch_stock_data_by_symbol(symbol):
    url = "https://nepse.ct.ws/"
    
    try:
        # Fetch the webpage content
        response = requests.get(url, verify=False)

        # Check for successful response
        if response.status_code != 200:
            print(f"Error: Unable to fetch data from nepse.ct.ws. Status code: {response.status_code}")
            return None

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Debugging: Print the raw HTML of the page to understand the structure
        print("Raw HTML from the website:")
        print(soup.prettify())  # This prints the complete HTML structure

        # Find the table that contains stock data
        table = soup.find('table')
        if not table:
            print("Error: No table found in the response.")
            return None

        # Extract rows from the table (skip the header row)
        rows = table.find_all('tr')[1:]  # Skip the first row (header)
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 12:  # Ensure there are enough columns
                continue  # Skip if the row doesn't have enough columns
            
            # Extract the stock symbol from the second column
            row_symbol = cols[1].text.strip()

            # Debugging: Check which symbol is being processed
            print(f"Checking symbol: {row_symbol}")

            if row_symbol.upper() == symbol.upper():
                # Extract stock data from the columns
                day_high = cols[4].text.strip()
                day_low = cols[5].text.strip()
                LTP = cols[2].text.strip()
                change_percent = cols[3].text.strip()
                volume = cols[7].text.strip()
                turnover = cols[8].text.strip()
                week_52_high = cols[9].text.strip()
                week_52_low = cols[10].text.strip()
                down_from_high = cols[11].text.strip()
                up_from_low = cols[12].text.strip()

                # Return the stock data
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
                    'Down from High': down_from_high,
                    'Up from Low': up_from_low
                }

        # If symbol is not found
        print(f"Symbol '{symbol}' not found.")
        return None

    except requests.exceptions.RequestException as e:
        # Handle any request exceptions (e.g., network issues)
        print(f"Error while fetching data: {e}")
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
    symbol = update.message.text.strip().upper()  # Ensure symbol is uppercase
    data = fetch_stock_data_by_symbol(symbol)

    if data:
        # Format the response if data is found
        response = (
            f"Stock Data for <b>{data['Symbol']}</b>:\n\n"
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
    else:
        # Response when symbol is not found
        response = f"स्टक सिम्बोल '{symbol}' फेला परेन।\nकृपया सही सिम्बोल दिनुहोस् वा फेरि प्रयास गर्नुहोस्।"

    # Send the response to the user
    await update.message.reply_text(response, parse_mode=ParseMode.HTML)

# Main function to set up the bot and run polling
if __name__ == "__main__":
    TOKEN = os.getenv("TELEGRAM_API_KEY")

    # Set up Telegram bot application
    application = ApplicationBuilder().token(TOKEN).build()

    # Add handlers to the application
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_stock_symbol))

    # Start polling
    print("Starting polling...")
    application.run_polling()  # Ensure your app is running here and will continue to listen for messages
