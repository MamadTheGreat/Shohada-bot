from flask import Flask, request
import os
from education import send_video, main_menu, disease_menu   # ماژول آموزش
from symptoms import send_symptom_menu, record_symptom       # ماژول علائم

app = Flask(__name__)

TOKEN = os.environ.get("BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()

    # پیام متنی
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")

        if text == "/start":
            send_video(chat_id, "files/as.mp4", "به ربات آموزشی بیمارستان شهدا خوش آمدید!")
            main_menu_keyboard = main_menu()
            send_symptom_menu(chat_id, main_menu_keyboard)

    # Callback Query (دکمه‌های اینلاین)
    if "callback_query" in update:
        cq = update["callback_query"]
        chat_id = cq["message"]["chat"]["id"]
        data = cq["data"]

        # ماژول آموزش
        if data.startswith("edu"):
            if data == "edu":
                send_video(chat_id, "files/as.mp4", "بیماری را انتخاب کنید:")
                keyboard = disease_menu()
                send_symptom_menu(chat_id, keyboard)
            else:
                send_video(chat_id, f"files/{data.split('_')[-1]}.mp4", f"آموزش {data.split('_')[-1]}")

        # ماژول علائم
        elif data.startswith("symptom"):
            record_symptom(chat_id, data)

    return "ok"

@app.route("/")
def home():
    return "Bot is running"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
