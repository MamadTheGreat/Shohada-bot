from flask import Flask, request
import os
import requests

# وارد کردن ماژول‌های خودتان
from symptoms import add_symptom, plot_symptoms
from education import handle_education

app = Flask(__name__)

TOKEN = os.environ.get("TELEGRAM_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}"

# ذخیره وضعیت کاربران
user_sessions = {}  # chat_id -> وضعیت فعلی ("main", "symptoms", "education")

# ارسال پیام متنی
def send_message(chat_id, text):
    try:
        url = f"{TELEGRAM_API_URL}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Error sending message: {e}")

# ارسال عکس
def send_photo(chat_id, photo_path, caption=""):
    try:
        url = f"{TELEGRAM_API_URL}/sendPhoto"
        with open(photo_path, "rb") as f:
            files = {"photo": f}
            data = {"chat_id": chat_id, "caption": caption}
            requests.post(url, files=files, data=data, timeout=10)
    except Exception as e:
        print(f"Error sending photo: {e}")

# مدیریت پیام کاربر
def handle_user_message(chat_id, text):
    if not text:
        return

    text = text.strip()

    # برگشت به منو اصلی
    if text.lower() == "منو":
        user_sessions[chat_id] = "main"
        send_message(chat_id, "منو اصلی:\n1. ثبت علائم\n2. آموزش")
        return

    # اگر کاربر تازه وارد است
    if chat_id not in user_sessions:
        user_sessions[chat_id] = "main"
        send_message(chat_id, "سلام! لطفا بخش مورد نظر را انتخاب کنید:\n1. ثبت علائم\n2. آموزش")
        return

    status = user_sessions[chat_id]

    if status == "main":
        if text == "1":
            user_sessions[chat_id] = "symptoms"
            send_message(chat_id, "لطفا نوع و مقدار علامت خود را وارد کنید، مثال:\nقند خون: 120")
        elif text == "2":
            user_sessions[chat_id] = "education"
            send_message(chat_id, "به بخش آموزش خوش آمدید. سوال یا موضوع خود را وارد کنید:")
        else:
            send_message(chat_id, "لطفا یکی از گزینه‌های منو را انتخاب کنید:\n1. ثبت علائم\n2. آموزش")

    elif status == "symptoms":
        try:
            # انتظار داریم کاربر پیام به شکل "نوع: مقدار" بده
            if ":" in text:
                symptom_type, value = map(str.strip, text.split(":", 1))
                add_symptom(chat_id, symptom_type, value)
                send_message(chat_id, f"علائم شما ثبت شد: {symptom_type} = {value}")

                # ساخت نمودار
                chart_path = plot_symptoms(chat_id)
                if chart_path:
                    send_photo(chat_id, chart_path, caption="تاریخچه علائم شما")
                else:
                    send_message(chat_id, "فعلا داده کافی برای نمودار وجود ندارد.")

            else:
                send_message(chat_id, "لطفا پیام خود را به شکل 'نوع: مقدار' وارد کنید، مثال:\nقند خون: 120")
        except Exception as e:
            send_message(chat_id, f"خطا در ثبت علائم: {e}")

        send_message(chat_id, "برای بازگشت به منو اصلی، 'منو' را تایپ کنید.")

    elif status == "education":
        try:
            response = handle_education(text)
            send_message(chat_id, response)
        except Exception as e:
            send_message(chat_id, f"خطا در بخش آموزش: {e}")
        send_message(chat_id, "برای بازگشت به منو اصلی، 'منو' را تایپ کنید.")

# دریافت پیام‌ها
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"].get("text", "")
            handle_user_message(chat_id, text)
    except Exception as e:
        print(f"Webhook error: {e}")
    return {"ok": True}

# ست کردن وب‌هوک
@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    try:
        url = f"{TELEGRAM_API_URL}/setWebhook?url={WEBHOOK_URL}/{TOKEN}"
        response = requests.get(url, timeout=5)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
