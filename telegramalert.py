# telegram_alert.py

import requests

TELEGRAM_BOT_TOKEN = '8308481495:AAHXLDhEiufFaEcLe_vMAQw1uRuUFpD49fg'
TELEGRAM_CHAT_ID = '6192169540'  # ← your actual chat ID

def send_telegram_alert(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    requests.post(url, json=payload)
