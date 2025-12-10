from flask import Flask, request
import requests
import json
import os

from education import send_video, main_menu, disease_menu
from symptoms import symptoms_menu, add_symptom, generate_chart, send_chart

TOKEN = os.environ.get("BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

app = Flask(__name__)

# ارسال پیام
def send_message(chat_id, text, reply_markup=None):
    url = BASE_URL + "sendMessage"
    data = {"chat_id": chat_id, "text": text}
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    requests.post(url, data=data)

# ---------------------
# دریافت مقدار علائم از کاربر
# ---------------------
user_states = {}  # ذخیره وضعیت کاربر برای وارد کردن مقدار

@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()
    chat_id = None
    text = None

    if "message" in update:
        msg = update["message"]
        chat_id = msg["chat"]["id"]
        text = msg.get("text", "")

        # بررسی اگر کاربر در حال وارد کردن مقدار باشد
        if chat_id in user_states:
            symptom_type = user_states[chat_id]
            try:
                value = float(text)
                add_symptom(chat_id, symptom_type, value)
                send_message(chat_id, f"{symptom_type} با موفقیت ثبت شد.", symptoms_menu())
            except:
                send_message(chat_id, "لطفا یک عدد معتبر وارد کنید.", symptoms_menu())
            del user_states[chat_id]
            return "ok"

        if text == "/start":
            send_message(chat_id, "به ربات آموزشی بیمارستان شهدا خوش آمدید.", main_menu())

    if "callback_query" in update:
        cq = update["callback_query"]
        chat_id = cq["message"]["chat"]["id"]
        data = cq["data"]

        # منوی اصلی
        if data == "edu":
            send_message(chat_id, "بیماری را انتخاب کنید:", disease_menu())
        elif data == "edu_diabetes":
            send_video(chat_id, "files/as.mp4", "آموزش دیابت نوع ۲")
        elif data == "edu_bp":
            send_video(chat_id, "files/aw.mp4", "آموزش فشار خون")
        elif data == "edu_heart":
            send_video(chat_id, "files/qw.mp4", "آموزش بیماری‌های قلبی")
        elif data == "symptoms":
            send_message(chat_id, "علائم مورد نظر را انتخاب کنید:", symptoms_menu())
        elif data == "blood_sugar":
            send_message(chat_id, "لطفا مقدار قند خون خود را وارد کنید:")
            user_states[chat_id] = "قند خون"
        elif data == "bp":
            send_message(chat_id, "لطفا مقدار فشار خون خود را وارد کنید:")
            user_states[chat_id] = "فشار خون"
        elif data == "weight":
            send_message(chat_id, "لطفا وزن خود را وارد کنید:")
            user_states[chat_id] = "وزن"
        elif data == "show_history":
            buf = generate_chart(chat_id)
            if buf:
                send_chart(chat_id, buf)
            else:
                send_message(chat_id, "هیچ داده‌ای برای نمایش وجود ندارد.", symptoms_menu())
        elif data == "back":
            send_message(chat_id, "منوی اصلی :", main_menu())

    return "ok"

@app.route("/")
def home():
    return "Bot is running"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
