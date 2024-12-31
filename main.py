import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import requests
from bs4 import BeautifulSoup

# .env फाइलबाट भेरिएबल लोड गर्नुहोस्
load_dotenv()

# Telegram Bot API टोकन र पोर्ट लोड गर्नुहोस्
BOT_TOKEN = os.getenv("TELEGRAM_BOT_API")
PORT = int(os.getenv("PORT"))

# NEPSE वेबसाइटबाट स्टोक डाटा स्क्र्याप गर्ने फङ्सन
def fetch_stock_data(symbol: str):
    url = f"https://nepse.ct.ws/{symbol}"  # URL को structure अनुसार यो अपडेट गर्नुहोस्
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # डाटा निकाल्ने प्रक्रिया यहाँ राख्नुहोस् (HTML संरचना अनुसार)
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
    except Exception as e:
        return {"Error": str(e)}

# /start कमाण्डको लागि ह्यान्डलर
def start(update: Update, context: CallbackContext):
    update.message.reply_text("नमस्कार! स्टोक सिम्बल पठाएर डाटा प्राप्त गर्नुहोस्।")

# सन्देशमा स्टोक सिम्बल खोज्न र डाटा ल्याउनको लागि ह्यान्डलर
def handle_message(update: Update, context: CallbackContext):
    text = update.message.text.strip()
    
    if text.isupper() and len(text) <= 5:  # सिम्बलको लागि निश्चित नियम (जस्तै, 1-5 अक्षर र ठूलो अक्षर)
        stock_data = fetch_stock_data(text)
        
        if "Error" in stock_data:
            update.message.reply_text(f"त्रुटि: {stock_data['Error']}")
        else:
            response = (
                f"Latest stock Data for <b>{stock_data['Symbol']}</b>:\n\n"
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
        update.message.reply_text("कृपया मान्य स्टोक सिम्बल (जस्तै ABC) पठाउनुहोस्।")

# मुख्य बोट फङ्सन
def main():
    # Updater र Dispatcher सेट गर्नुहोस्
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # कमाण्ड ह्यान्डलरहरू
    dispatcher.add_handler(CommandHandler('start', start))

    # सन्देश ह्यान्डलर: स्टोक सिम्बल प्राप्त गर्ने
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # बोट सुरु गर्नुहोस्
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
