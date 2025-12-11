from flask import Flask, request
import os
import requests
from symptoms import add_symptom, plot_symptoms
from education import handle_education

app = Flask(__name__)

# دریافت توکن و آدرس‌ها از متغیرهای محیطی
TOKEN = os.environ.get("TELEGRAM_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}"

# حافظه موقت کاربران
user_sessions = {}

def send_message(chat_id, text):
    """ارسال پیام متنی به کاربر"""
    try:
        url = f"{TELEGRAM_API_URL}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Error sending message: {e}")

def send_photo(chat_id, photo_path, caption=""):
    """ارسال عکس (نمودار) به کاربر"""
    try:
        url = f"{TELEGRAM_API_URL}/sendPhoto"
        with open(photo_path, "rb") as f:
            files = {"photo": f}
            data = {"chat_id": chat_id, "caption": caption}
            requests.post(url, files=files, data=data, timeout=20)
    except Exception as e:
        print(f"Error sending photo: {e}")

def handle_user_message(chat_id, text):
    if not text:
        return

    text = text.strip()

    # دکمه بازگشت یا منو
    if text == "/start" or text.lower() == "منو":
        user_sessions[chat_id] = "main"
        send_message(chat_id, "منو اصلی:\n1. ثبت علائم 📝\n2. آموزش 📘")
        return

    # تعیین وضعیت پیش‌فرض برای کاربر جدید
    if chat_id not in user_sessions:
        user_sessions[chat_id] = "main"
        send_message(chat_id, "سلام! لطفا بخش مورد نظر را انتخاب کنید:\n1. ثبت علائم\n2. آموزش")
        return

    status = user_sessions[chat_id]

    # --- بخش منوی اصلی ---
    if status == "main":
        if text == "1":
            user_sessions[chat_id] = "symptoms"
            send_message(chat_id, "وارد بخش ثبت علائم شدید.\nلطفا نوع و مقدار را با دو نقطه جدا کنید.\nمثال:\nقند خون: 120\nفشار خون: 12\nوزن: 80")
        elif text == "2":
            user_sessions[chat_id] = "education"
            send_message(chat_id, "به بخش آموزش خوش آمدید.\nموضوع خود را بنویسید (مثلاً: دیابت، فشار خون، قلب):")
        else:
            send_message(chat_id, "لطفا عدد 1 یا 2 را ارسال کنید.")

    # --- بخش ثبت علائم ---
    elif status == "symptoms":
        if ":" in text:
            try:
                # جدا کردن متن با اولین دو نقطه
                parts = text.split(":", 1)
                symptom_type = parts[0].strip()
                value = parts[1].strip()

                # تلاش برای ثبت در گوگل شیت
                if add_symptom(chat_id, symptom_type, value):
                    send_message(chat_id, f"✅ {symptom_type} با مقدار {value} ثبت شد.")
                    
                    # رسم و ارسال نمودار
                    send_message(chat_id, "⏳ در حال ترسیم نمودار...")
                    chart_path = plot_symptoms(chat_id)
                    if chart_path and os.path.exists(chart_path):
                        send_photo(chat_id, chart_path, caption="تاریخچه نموداری شما")
                    else:
                        send_message(chat_id, "داده کافی برای رسم نمودار وجود ندارد یا خطایی رخ داد.")
                else:
                    send_message(chat_id, "❌ خطا در اتصال به دیتابیس (گوگل شیت).")
            
            except Exception as e:
                print(f"Error processing symptom: {e}")
                send_message(chat_id, "خطا در پردازش. لطفا طبق الگو ارسال کنید.")
        else:
            send_message(chat_id, "فرمت نادرست است. مثال:\nقند خون: 120")
        
        send_message(chat_id, "برای خروج 'منو' را بنویسید.")

    # --- بخش آموزش ---
    elif status == "education":
        response = handle_education(text)
        send_message(chat_id, response)
        send_message(chat_id, "برای خروج 'منو' را بنویسید.")

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

@app.route("/", methods=["GET"])
def home():
    return "Bot is running!"

@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    try:
        url = f"{TELEGRAM_API_URL}/setWebhook?url={WEBHOOK_URL}/{TOKEN}"
        response = requests.get(url, timeout=5)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
