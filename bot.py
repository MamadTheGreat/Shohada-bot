import os
import requests
import json
import time

# ===============================
# دریافت توکن از محیط سیستم (امن)
# ===============================
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise Exception("BOT_TOKEN not set in environment variables")

BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"
last_update_id = None

# ===============================
# توابع API
# ===============================
def send_message(chat_id, text, reply_markup=None):
    url = BASE_URL + "sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    try:
        requests.post(url, data=payload, timeout=10)
    except:
        pass

def answer_callback(callback_query_id):
    url = BASE_URL + "answerCallbackQuery"
    payload = {"callback_query_id": callback_query_id}
    try:
        requests.post(url, data=payload, timeout=10)
    except:
        pass

def get_updates():
    global last_update_id
    try:
        url = BASE_URL + "getUpdates"
        params = {}
        if last_update_id:
            params["offset"] = last_update_id + 1
        r = requests.get(url, params=params, timeout=10)
        return r.json()
    except:
        return {"ok": False, "result": []}

# ===============================
# کیبوردها
# ===============================
def main_menu():
    return {
        "inline_keyboard": [
            [{"text": "📘 آموزش بیماری‌ها", "callback_data": "edu"}],
            [{"text": "📝 ثبت علائم", "callback_data": "symptoms"}],
            [{"text": "👤 اتصال به کارشناس", "callback_data": "expert"}]
        ]
    }

def disease_menu():
    return {
        "inline_keyboard": [
            [{"text": "دیابت نوع ۲", "callback_data": "edu_diabetes"}],
            [{"text": "فشار خون", "callback_data": "edu_bp"}],
            [{"text": "بیماری‌های قلبی", "callback_data": "edu_heart"}],
            [{"text": "⬅️ بازگشت", "callback_data": "back"}]
        ]
    }

# ===============================
# پردازش آپدیت‌ها
# ===============================
def handle_update(update):
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        if text == "/start":
            send_message(chat_id, "✅ به ربات آموزشی بیمارستان شهدا خوش آمدید.", reply_markup=main_menu())

    if "callback_query" in update:
        cq = update["callback_query"]
        data = cq["data"]
        chat_id = cq["message"]["chat"]["id"]
        answer_callback(cq["id"])

        if data == "edu":
            send_message(chat_id, "یک بیماری را انتخاب کنید:", reply_markup=disease_menu())
        elif data == "edu_diabetes":
            send_message(chat_id, "📄 لینک آموزش دیابت:\nhttps://drive.google.com/uc?id=11mrRtXtUVY9IxOSxH0Y40nRLzkC8MtN1")
        elif data == "edu_bp":
            send_message(chat_id, "📄 لینک آموزش فشار خون:\nhttps://drive.google.com/uc?id=1f81sHOgCRfpUJFBAHJSuRgfWQwaTklZs")
        elif data == "edu_heart":
            send_message(chat_id, "📄 لینک آموزش بیماری‌های قلبی:\nhttps://drive.google.com/uc?id=1f81sHOgCRfpUJFBAHJSuRgfWQwaTklZs")
        elif data == "back":
            send_message(chat_id, "بازگشت به منوی اصلی:", reply_markup=main_menu())

# ===============================
# اجرای ربات
# ===============================
def run_bot():
    global last_update_id
    print("✅ Bot is running...")
    while True:
        updates = get_updates()
        if updates.get("ok"):
            for update in updates["result"]:
                last_update_id = update["update_id"]
                handle_update(update)
        time.sleep(1)

if __name__ == "__main__":
    run_bot()
