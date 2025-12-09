from flask import Flask, request
import requests
import json

TOKEN = "توکن_خود8537033981:AAF0vQ2NOReID6uKaqQmrAH9v_IMa3yy5hw"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

app = Flask(__name__)

def send_message(chat_id, text, reply_markup=None):
    url = BASE_URL + "sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text
    }
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    requests.post(url, data=data)

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
            [{"text": "⬅ بازگشت", "callback_data": "back"}]
        ]
    }

@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()

    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")

        if text == "/start":
            send_message(chat_id, "به ربات آموزشی بیمارستان شهدا خوش آمدید.", main_menu())

    if "callback_query" in update:
        cq = update["callback_query"]
        chat_id = cq["message"]["chat"]["id"]
        data = cq["data"]

        if data == "edu":
            send_message(chat_id, "بیماری را انتخاب کنید:", disease_menu())
        elif data == "edu_diabetes":
            send_message(chat_id, "لینک آموزش دیابت:\nhttps://drive.google.com/...")
        elif data == "edu_bp":
            send_message(chat_id, "لینک آموزش فشار خون:\nhttps://drive.google.com/...")
        elif data == "edu_heart":
            send_message(chat_id, "لینک آموزش بیماری‌های قلبی:\nhttps://drive.google.com/...")
        elif data == "back":
            send_message(chat_id, "منوی اصلی :", main_menu())

    return "ok"

@app.route("/")
def home():
    return "Bot is running"
