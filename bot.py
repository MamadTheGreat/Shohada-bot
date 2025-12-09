from flask import Flask, request
import requests
import os

TOKEN = os.environ.get("BOT_TOKEN")  # از Render می‌خونه
API_URL = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)

# ---------- ابزار ارسال پیام ----------
def send_message(chat_id, text, reply_markup=None):
    url = f"{API_URL}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    if reply_markup:
        data["reply_markup"] = reply_markup
    requests.post(url, json=data)

# ---------- منوها ----------
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
            [{"text": "بازگشت", "callback_data": "back"}]
        ]
    }

# ---------- دریافت پیام از تلگرام ----------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    # پیام معمولی
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send_message(chat_id, "به ربات آموزشی بیمارستان شهدا خوش آمدید.", reply_markup=main_menu())

    # کلیک روی دکمه منو
    if "callback_query" in data:
        cq = data["callback_query"]
        chat_id = cq["message"]["chat"]["id"]
        data = cq["data"]

        if data == "edu":
            send_message(chat_id, "یک بیماری را انتخاب کنید:", reply_markup=disease_menu())

        elif data == "edu_diabetes":
            send_message(chat_id, "لینک آموزش دیابت: ...")

        elif data == "edu_bp":
            send_message(chat_id, "لینک آموزش فشار خون: ...")

        elif data == "edu_heart":
            send_message(chat_id, "لینک آموزش قلب: ...")

        elif data == "back":
            send_message(chat_id, "بازگشت به منوی اصلی:", reply_markup=main_menu())

    return "OK", 200

# ---------- تست سلامت سرور ----------
@app.route("/")
def home():
    return "Bot is running!"

# ---------- اجرا ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
