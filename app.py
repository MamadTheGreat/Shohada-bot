from flask import Flask, request
import requests

TOKEN = "bot425065:8ee73c44-f658-4cff-bbb7-a0b25bfe4310"
BASE_URL = f"https://api.eitaa.com/bot{TOKEN}/"

app = Flask(__name__)

# لینک‌های آموزشی (مثال)
EDU_LINKS = {
    "edu_diab": "https://your-google-drive-link-diabetes",
    "edu_bp": "https://your-google-drive-link-bp",
    "edu_heart": "https://your-google-drive-link-heart"
}

# ---------------------------
# توابع کمکی
# ---------------------------
def send_message(chat_id, text, reply_markup=None):
    url = BASE_URL + "sendMessage"
    data = {"chat_id": chat_id, "text": text}
    if reply_markup:
        data["reply_markup"] = reply_markup
    requests.post(url, json=data)


def get_main_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "📘 آموزش بیماری‌ها", "callback_data": "edu"}],
            [{"text": "📝 ثبت علائم", "callback_data": "symptoms"}],
            [{"text": "👤 اتصال به کارشناس", "callback_data": "expert"}]
        ]
    }


def get_edu_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "دیابت نوع ۲", "callback_data": "edu_diab"}],
            [{"text": "فشار خون", "callback_data": "edu_bp"}],
            [{"text": "بیماری‌های قلبی", "callback_data": "edu_heart"}],
            [{"text": "بازگشت 🔙", "callback_data": "back"}]
        ]
    }

# ---------------------------
# مسیر webhook
# ---------------------------
@app.route("/", methods=["POST"])
def webhook():
    data = request.json

    if "chat" in data:  # پیام ساده
        chat_id = data["chat"]["id"]
        text = data.get("text", "")
        if text.lower() in ["/start", "شروع"]:
            send_message(chat_id, "سلام 👋\nبه ربات آموزشی خوش آمدید!\nلطفاً یک گزینه را انتخاب کنید:", reply_markup=get_main_keyboard())

    elif "callback_query" in data:  # دکمه‌های منوی کشویی
        cq = data["callback_query"]
        chat_id = cq["message"]["chat"]["id"]
        data_cb = cq["data"]

        if data_cb == "edu":
            send_message(chat_id, "لطفاً بیماری مورد نظر را انتخاب کنید:", reply_markup=get_edu_keyboard())
        elif data_cb in EDU_LINKS:
            send_message(chat_id, f"فایل آموزشی:\n{EDU_LINKS[data_cb]}")
        elif data_cb == "symptoms":
            send_message(chat_id, "لطفاً علائم خود را ارسال کنید.")
        elif data_cb == "expert":
            send_message(chat_id, "در حال اتصال به کارشناس…")
        elif data_cb == "back":
            send_message(chat_id, "بازگشت به منوی اصلی:", reply_markup=get_main_keyboard())

    return "ok"

# ---------------------------
# اجرای سرور
# ---------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
