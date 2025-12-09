from flask import Flask, request
import requests
import json
import os

TOKEN = os.environ.get("BOT_TOKEN")  # امن
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

def send_video(chat_id, video_path, caption=None):
    url = BASE_URL + "sendVideo"
    files = {"video": open(video_path, "rb")}
    data = {"chat_id": chat_id}
    if caption:
        data["caption"] = caption
    requests.post(url, data=data, files=files)

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
            send_video(chat_id, "files/as.mp4", "آموزش دیابت نوع ۲")
        elif data == "edu_bp":
            send_video(chat_id, "files/aw.mp4", "آموزش فشار خون")
        elif data == "edu_heart":
            send_video(chat_id, "files/qw.mp4", "آموزش بیماری‌های قلبی")
        elif data == "back":
            send_message(chat_id, "منوی اصلی :", main_menu())

    return "ok"

@app.route("/")
def home():
    return "Bot is running"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
