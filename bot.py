from flask import Flask, request
import os
import requests
import json
import time

# وارد کردن ماژول‌های خودتان
from symptoms import add_symptom, plot_symptoms
from education import get_main_menu_keyboard, get_education_menu_keyboard, get_symptoms_nav_keyboard, handle_education # توابع کیبورد جدید به‌روز شدند

app = Flask(name)

# --- تنظیمات عمومی ---
TOKEN = os.environ.get("TELEGRAM_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}"
WEBHOOK_PATH = f"/{TOKEN}"

# ذخیره وضعیت کاربران
user_sessions = {}

# --- توابع کمکی ---
def send_message(chat_id, text, reply_markup=None):
    """ارسال پیام متنی با پشتیبانی از دکمه‌های کیبوردی (Reply Keyboard)"""
    try:
        url = f"{TELEGRAM_API_URL}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        if reply_markup:
            # تلگرام نیاز دارد که reply_markup به صورت یک رشته JSON باشد
            payload["reply_markup"] = json.dumps(reply_markup)
            
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

# --- مدیریت پیام کاربر ---
def handle_user_message(chat_id, text):
    if not text:
        return

    text = text.strip()
    
    # مدیریت بازگشت به منوی اصلی
    if text == "➡️ بازگشت به منو اصلی":
        user_sessions[chat_id] = "main"
        send_message(chat_id, "به منوی اصلی بازگشتید. بخش مورد نظر خود را انتخاب کنید.", reply_markup=get_main_menu_keyboard())
        return

    # اگر کاربر تازه وارد است یا درخواست /start می‌دهد
    if text == "/start" or chat_id not in user_sessions:
        user_sessions[chat_id] = "main"
        send_message(chat_id, "به ربات خوش آمدید. بخش مورد نظر خود را انتخاب کنید.", reply_markup=get_main_menu_keyboard())
        return

    status = user_sessions.get(chat_id, "main")

    # --- بخش منوی اصلی (مدیریت دکمه‌ها) ---
    if status == "main":
        if text == "📝 ثبت علائم":
            user_sessions[chat_id] = "symptoms"
            # نمایش کیبورد بازگشت در بخش علائم
            send_message(chat_id, "وارد بخش ثبت علائم شدید.\nلطفا نوع و مقدار را با دو نقطه جدا کنید.\nمثال:\nقند خون: 120", reply_markup=get_symptoms_nav_keyboard())
        
        elif text == "📘 آموزش":
            user_sessions[chat_id] = "education"
            # نمایش کیبورد آموزشی
            send_message(chat_id, "به بخش آموزش خوش آمدید.\nموضوع مورد نظر خود را از لیست زیر انتخاب کنید:", reply_markup=get_education_menu_keyboard())

        elif text == "👤 اتصال به کارشناس":
            send_message(chat_id, "این قابلیت در دست توسعه است. لطفا از منو اصلی استفاده کنید.", reply_markup=get_main_menu_keyboard())

        else:
            send_message(chat_id, "لطفا از دکمه‌های منو اصلی استفاده کنید.", reply_markup=get_main_menu_keyboard())


    # --- بخش ثبت علائم ---
    elif status == "symptoms":
        if ":" in text:
            try:
                parts = text.split(":", 1)
                symptom_type = parts[0].strip()
                value = parts[1].strip()

                if add_symptom(chat_id, symptom_type, value):
                    send_message(chat_id, f"✅ {symptom_type} با مقدار {value} ثبت شد.", reply_markup=get_symptoms_nav_keyboard())
                    
                    send_message(chat_id, "⏳ در حال ترسیم نمودار...", reply_markup=get_symptoms_nav_keyboard())
                    time.sleep(1)
                    chart_path = plot_symptoms(chat_id)
                    if chart_path and os.path.exists(chart_path):
                        send_photo(chat_id, chart_path, caption="تاریخچه نموداری شما")
                        os.remove(chart_path)
                    else:
                        send_message(chat_id, "داده کافی برای رسم نمودار وجود ندارد یا خطایی رخ داد.", reply_markup=get_symptoms_nav_keyboard())
                else:
                    send_message(chat_id, "❌ خطا در اتصال به دیتابیس (گوگل شیت).", reply_markup=get_symptoms_nav_keyboard())
            
            except Exception as e:
                print(f"Error processing symptom: {e}")
                send_message(chat_id, "خطا در پردازش. لطفا طبق الگو ارسال کنید.", reply_markup=get_symptoms_nav_keyboard())
        else:
            send_message(chat_id, "فرمت نادرست است. لطفا طبق مثال زیر عمل کنید:\nقند خون: 120", reply_markup=get_symptoms_nav_keyboard())


    # --- بخش آموزش ---
    elif status == "education":
        response = handle_education(text)
        send_message(chat_id, response, reply_markup=get_education_menu_keyboard())

# --- مدیریت Webhook (دریافت پیام‌ها) ---
@app.route(WEBHOOK_PATH, methods=["POST"])
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

# --- ست کردن وب‌هوک ---
@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    try:
        url = f"{TELEGRAM_API_URL}/setWebhook?url={WEBHOOK_URL}{WEBHOOK_PATH}"
        response = requests.get(url, timeout=5)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# --- اجرای برنامه ---
if name == "main":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
