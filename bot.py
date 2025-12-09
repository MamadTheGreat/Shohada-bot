# bot.py
from flask import Flask, request
import requests
import json
import os

from education import send_video, main_menu, disease_menu   # ماژول آموزش
from symptoms import symptoms_menu, record_symptom, generate_history_chart, user_state  # ماژول علائم

TOKEN = os.environ.get("BOT_TOKEN")  # امن
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

app = Flask(__name__)

# ------------------------------
# توابع کمکی
# ------------------------------
def send_message(chat_id, text, reply_markup=None):
    url = BASE_URL + "sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text
    }
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    requests.post(url, data=data)

def send_photo(chat_id, photo_path, caption=None):
    url = BASE_URL + "sendPhoto"
    files = {"photo": open(photo_path, "rb")}
    data = {"chat_id": chat_id}
    if caption:
        data["caption"] = caption
    requests.post(url, data=data, files=files)

# ------------------------------
# webhook
# ------------------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()

    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")

        # شروع ربات
        if text == "/start":
            send_message(chat_id, "به ربات آموزشی بیمارستان شهدا خوش آمدید.", main_menu())

        # اگر کاربر در حالت وارد کردن مقدار علائم است
        elif chat_id in user_state:
            symptom = user_state[chat_id]["symptom"]
            try:
                value = float(text.replace(",", "."))  # مقدار عددی
                record_symptom(chat_id, symptom, value)
                send_message(chat_id, f"{symptom} با مقدار {value} ثبت شد.", symptoms_menu())
                del user_state[chat_id]
            except ValueError:
                send_message(chat_id, "لطفا یک عدد معتبر وارد کنید:")

    if "callback_query" in update:
        cq = update["callback_query"]
        chat_id = cq["message"]["chat"]["id"]
        data = cq["data"]

        # ---------- آموزش ----------
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

        # ---------- ثبت علائم ----------
        elif data == "symptoms":
            send_message(chat_id, "علائم را انتخاب کنید:", symptoms_menu())
        elif data in ["sugar", "bp", "weight"]:
            user_state[chat_id] = {"symptom": data}
            send_message(chat_id, f"لطفا مقدار {data} را وارد کنید:")
        elif data == "history":
            chart_path = generate_history_chart(chat_id)
            if chart_path:
                send_photo(chat_id, chart_path, "تاریخچه علائم شما")
            else:
                send_message(chat_id, "هیچ تاریخی ثبت نشده است.")
        elif data == "back":
            send_message(chat_id, "منوی اصلی :", main_menu())

    return "ok"

@app.route("/")
def home():
    return "Bot is running"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
