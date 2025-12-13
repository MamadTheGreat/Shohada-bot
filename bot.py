from flask import Flask, request
import requests
import os

from education import (
    main_menu_keyboard,
    disease_menu_keyboard,
    diabetes_menu_keyboard
)
from symptoms import add_symptom, plot_symptoms

app = Flask(__name__)

TOKEN = os.environ.get("TELEGRAM_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
TG_URL = f"https://api.telegram.org/bot{TOKEN}"
WEBHOOK_PATH = f"/webhook/{TOKEN}"

user_state = {}

def send_message(chat_id, text, keyboard=None):
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    if keyboard:
        payload["reply_markup"] = keyboard
    requests.post(f"{TG_URL}/sendMessage", json=payload)

@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    data = request.json
    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")

    # start
    if text == "/start":
        user_state[chat_id] = "MAIN"
        send_message(
            chat_id,
            "سلام 🌱\nبه ربات پایش سلامت خوش آمدید",
            main_menu_keyboard()
        )
        return "ok"

    # منوی اصلی
    if text == "انتخاب بیماری":
        user_state[chat_id] = "DISEASE"
        send_message(chat_id, "بیماری را انتخاب کنید:", disease_menu_keyboard())
        return "ok"

    if text == "دیابت":
        user_state[chat_id] = "DIABETES"
        send_message(chat_id, "منوی دیابت:", diabetes_menu_keyboard())
        return "ok"

    # ثبت علائم
    if text == "ثبت علائم":
        user_state[chat_id] = "SYMPTOM_MENU"
        send_message(
            chat_id,
            "کدام مورد را ثبت می‌کنید؟",
            {
                "keyboard": [
                    ["قند خون"],
                    ["فشار خون"],
                    ["وزن"],
                    ["بازگشت"]
                ],
                "resize_keyboard": True
            }
        )
        return "ok"

    if text == "قند خون":
        user_state[chat_id] = "WAIT_SUGAR"
        send_message(chat_id, "عدد قند خون (mg/dl) را وارد کنید:")
        return "ok"

    if text == "وزن":
        user_state[chat_id] = "WAIT_WEIGHT"
        send_message(chat_id, "وزن (kg) را وارد کنید:")
        return "ok"

    if text == "فشار خون":
        user_state[chat_id] = "WAIT_BP_SYS"
        send_message(chat_id, "عدد سیستول را وارد کنید:")
        return "ok"

    # دریافت اعداد
    if user_state.get(chat_id) == "WAIT_SUGAR":
        add_symptom(chat_id, "sugar", text)
        send_message(chat_id, "✅ ثبت شد", diabetes_menu_keyboard())
        user_state[chat_id] = "DIABETES"
        return "ok"

    if user_state.get(chat_id) == "WAIT_WEIGHT":
        add_symptom(chat_id, "weight", text)
        send_message(chat_id, "✅ ثبت شد", diabetes_menu_keyboard())
        user_state[chat_id] = "DIABETES"
        return "ok"

    if user_state.get(chat_id) == "WAIT_BP_SYS":
        user_state[chat_id] = f"WAIT_BP_DIA:{text}"
        send_message(chat_id, "عدد دیاستول را وارد کنید:")
        return "ok"

    if user_state.get(chat_id, "").startswith("WAIT_BP_DIA"):
        sys = user_state[chat_id].split(":")[1]
        dia = text
        add_symptom(chat_id, "blood_pressure", f"{sys}/{dia}")
        send_message(chat_id, "✅ ثبت شد", diabetes_menu_keyboard())
        user_state[chat_id] = "DIABETES"
        return "ok"

    # نمودار
    if text == "نمایش نمودار":
        path = plot_symptoms(chat_id)
        if path:
            with open(path, "rb") as f:
                requests.post(
                    f"{TG_URL}/sendPhoto",
                    data={"chat_id": chat_id},
                    files={"photo": f}
                )
        else:
            send_message(chat_id, "داده‌ای برای نمایش وجود ندارد")
        return "ok"

    if text == "بازگشت":
        user_state[chat_id] = "MAIN"
        send_message(chat_id, "منوی اصلی:", main_menu_keyboard())
        return "ok"

    send_message(chat_id, "دستور نامعتبر ❌")
    return "ok"

@app.route("/set_webhook")
def set_webhook():
    return requests.get(
        f"{TG_URL}/setWebhook",
        params={"url": WEBHOOK_URL + WEBHOOK_PATH}
    ).json()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
