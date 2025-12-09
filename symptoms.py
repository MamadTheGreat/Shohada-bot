# symptoms.py
from flask import Flask, request
import requests
import json
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import matplotlib.pyplot as plt

TOKEN = os.environ.get("BOT_TOKEN")  # توکن امن
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

GOOGLE_JSON = "config/google_key.json"

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_JSON, scope)
client = gspread.authorize(creds)

app = Flask(__name__)

# ----------------------
# state کاربر
# ----------------------
user_state = {}  # chat_id -> last_selected_symptom

# ----------------------
# توابع تلگرام
# ----------------------
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

# ----------------------
# منوها
# ----------------------
def symptoms_menu():
    return {
        "inline_keyboard": [
            [{"text": "💉 قند خون", "callback_data": "sugar"}],
            [{"text": "🩸 فشار خون", "callback_data": "bp"}],
            [{"text": "⚖ وزن", "callback_data": "weight"}],
            [{"text": "📊 مشاهده تاریخچه", "callback_data": "history"}],
            [{"text": "⬅ بازگشت", "callback_data": "back"}]
        ]
    }

# ----------------------
# Google Sheets helper
# ----------------------
def get_user_sheet(chat_id):
    try:
        sheet = client.open(str(chat_id)).sheet1
    except gspread.SpreadsheetNotFound:
        sheet = client.create(str(chat_id)).sheet1
        sheet.append_row(["Datetime", "Sugar", "BP", "Weight"])
    return sheet

def record_symptom(chat_id, symptom, value):
    sheet = get_user_sheet(chat_id)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # آخرین ردیف
    last_row = sheet.get_all_values()[-1] if len(sheet.get_all_values()) > 1 else ["", "", "", ""]
    sugar, bp, weight = last_row[1], last_row[2], last_row[3]

    if symptom == "sugar":
        sugar = value
    elif symptom == "bp":
        bp = value
    elif symptom == "weight":
        weight = value

    sheet.append_row([now, sugar, bp, weight])

def generate_history_chart(chat_id):
    sheet = get_user_sheet(chat_id)
    data = sheet.get_all_values()[1:]  # حذف هدر
    if not data:
        return None

    times = [row[0] for row in data]
    sugars = [float(row[1]) if row[1] else None for row in data]
    bps = [float(row[2]) if row[2] else None for row in data]
    weights = [float(row[3]) if row[3] else None for row in data]

    plt.figure(figsize=(10, 5))
    if any(sugars):
        plt.plot(times, sugars, label="Sugar")
    if any(bps):
        plt.plot(times, bps, label="BP")
    if any(weights):
        plt.plot(times, weights, label="Weight")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    
    chart_path = f"{chat_id}_history.png"
    plt.savefig(chart_path)
    plt.close()
    return chart_path

# ----------------------
# webhook handler
# ----------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()
    chat_id = None

    # callback query
    if "callback_query" in update:
        cq = update["callback_query"]
        chat_id = cq["message"]["chat"]["id"]
        data = cq["data"]

        if data == "symptoms":
            send_message(chat_id, "ثبت یا مشاهده علائم خود را انتخاب کنید:", symptoms_menu())
        elif data in ["sugar", "bp", "weight"]:
            user_state[chat_id] = data  # ذخیره آخرین علامت انتخاب شده
            send_message(chat_id, f"مقدار {data} خود را ارسال کنید:")
        elif data == "history":
            chart = generate_history_chart(chat_id)
            if chart:
                send_photo(chat_id, chart, "تاریخچه علائم شما")
            else:
                send_message(chat_id, "فعلا داده‌ای برای نمایش وجود ندارد.")
        elif data == "back":
            send_message(chat_id, "بازگشت به منوی اصلی.", main_menu())

    # پیام متنی
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")

        if chat_id in user_state and text.replace(".", "").isdigit():
            symptom = user_state[chat_id]
            record_symptom(chat_id, symptom, text)
            send_message(chat_id, f"مقدار {symptom} شما ثبت شد.")
            user_state.pop(chat_id)  # پاک کردن state بعد از ثبت

    return "ok"

@app.route("/")
def home():
    return "Bot Symptoms Module Running"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
