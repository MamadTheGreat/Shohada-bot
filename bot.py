from flask import Flask, request
import os
from education import send_video, main_menu, disease_menu
from symptoms import symptoms_menu, handle_symptom_input, show_history

TOKEN = os.environ.get("BOT_TOKEN")  # توکن ربات
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

app = Flask(__name__)

# ارسال پیام ساده
def send_message(chat_id, text, reply_markup=None):
    import requests, json
    url = BASE_URL + "sendMessage"
    data = {"chat_id": chat_id, "text": text}
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    requests.post(url, data=data)

# ذخیره وضعیت کاربر برای دریافت ورودی
user_state = {}  # chat_id -> {"expecting": None}

@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()

    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")

        # دستور /start
        if text == "/start":
            send_message(chat_id, "به ربات آموزشی بیمارستان شهدا خوش آمدید.", main_menu())
            user_state.pop(chat_id, None)
            return "ok"

        # دریافت مقدار علائم
        if chat_id in user_state and user_state[chat_id].get("expecting"):
            handle_symptom_input(chat_id, text, user_state)
            return "ok"

    if "callback_query" in update:
        cq = update["callback_query"]
        chat_id = cq["message"]["chat"]["id"]
        data = cq["data"]

        # منوها
        if data == "edu":
            send_message(chat_id, "بیماری را انتخاب کنید:", disease_menu())
        elif data.startswith("edu_"):
            send_video(chat_id, data)
        elif data == "symptoms":
            send_message(chat_id, "علائم را انتخاب کنید:", symptoms_menu())
        elif data in ["sym_blood", "sym_bp", "sym_weight"]:
            user_state[chat_id] = {"expecting": data}
            send_message(chat_id, f"مقدار {data} را وارد کنید:")
        elif data == "sym_history":
            show_history(chat_id)
        elif data == "back":
            send_message(chat_id, "منوی اصلی :", main_menu())

    return "ok"

@app.route("/")
def home():
    return "Bot is running"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
