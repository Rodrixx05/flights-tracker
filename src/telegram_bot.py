import os
import requests

def send_telegram_message(text):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("Avís: TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID no estan definits. Missatge no enviat.")
        return
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    # Telegram API limit is 4096. If message is longer, we should split it.
    # For now, we assume route messages are < 4096 chars.
    
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    response = requests.post(url, json=payload, timeout=10)
    if response.status_code != 200:
        print(f"Error enviant Telegram: {response.text}")
    else:
        print("Missatge enviat correctament a Telegram.")
