from flask import Flask, request
import requests
import json
import os
from education import send_video, main_menu, disease_menu
from symptoms import add_symptom, plot_symptoms

TOKEN = os.environ.get("BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

app = Flask(__name__)

# وضعیت کاربران: chat_id -> علامتی که در حال ثبت است
user_state = {}

def send_message(chat_id, text, reply_markup=None):
    url = BASE_URL + "sendMessage"
    data = {"chat_id": chat_id, "text": text}
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

@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()

    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")

        # اگر کاربر در حالت ثبت علامت باشد، مقدار را ثبت کن
        if chat_id in user_state:
            symptom_type = user_state.pop(chat_id)  # علامت جاری
            try:
                value = float(text)
                add_symptom(chat_id, symptom_type, value)
                send_message(chat_id, f"{symptom_type} شما با مقدار {value} ثبت شد.")
            except ValueError:
                send_message(chat_id, "لطفاً یک عدد معتبر وارد کنید.")
        elif text == "/start":
            send_message(chat_id, "به ربات آموزشی بیمارستان شهدا خوش آمدید.", main_menu())

    if "callback_query" in update:
        cq = update["callback_query"]
        chat_id = cq["message"]["chat"]["id"]
        data = cq["data"]

        # === آموزش ===
        if data.startswith("edu"):
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

        # === ثبت علائم ===
        elif data.startswith("symp"):
            if data == "symptoms":
                reply = {
                    "inline_keyboard": [
                        [{"text": "قند خون", "callback_data": "symp_sugar"}],
                        [{"text": "فشار خون", "callback_data": "symp_bp"}],
                        [{"text": "وزن", "callback_data": "symp_weight"}],
                        [{"text": "📊 مشاهده تاریخچه علائم", "callback_data": "symp_history"}],
                        [{"text": "⬅ بازگشت", "callback_data": "back"}]
                    ]
                }
                send_message(chat_id, "علائم را انتخاب کنید:", reply)
            elif data == "symp_history":
                img_path = plot_symptoms(chat_id)
                if img_path:
                    send_photo(chat_id, img_path, "تاریخچه علائم شما")
                else:
                    send_message(chat_id, "هیچ رکوردی برای شما ثبت نشده است.")
            elif data in ["symp_sugar", "symp_bp", "symp_weight"]:
                # کاربر الان در حالت ثبت این علامت است
                symptom_map = {
                    "symp_sugar": "قند خون",
                    "symp_bp": "فشار خون",
                    "symp_weight": "وزن"
                }
                user_state[chat_id] = symptom_map[data]
                send_message(chat_id, f"لطفاً مقدار {symptom_map[data]} خود را وارد کنید:")

    return "ok"

@app.route("/")
def home():
    return "Bot is running"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
