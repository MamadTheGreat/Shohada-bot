import os
import requests

TOKEN = os.environ.get("BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

def telegram_post(method, data=None, files=None):
    url = BASE_URL + method
    try:
        resp = requests.post(url, data=data, files=files, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"Telegram API error ({method}):", e)
        return None
