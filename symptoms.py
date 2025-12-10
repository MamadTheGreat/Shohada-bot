import os
import datetime
import io
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import matplotlib.pyplot as plt
import requests
import json

TOKEN = os.environ.get("BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

CREDS_PATH = os.path.join("config", "google_sa.json")

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_PATH, scope)
gc = gspread.authorize(creds)

# ---------------------
# منوها
# ---------------------
def symptoms_menu():
    return {
        "inline_keyboard": [
            [{"text": "قند خون", "callback_data": "blood_sugar"}],
            [{"text": "فشار خون", "callback_data": "bp"}],
            [{"text": "وزن", "callback_data": "weight"}],
            [{"text": "📊 مشاهده تاریخچه علائم", "callback_data": "show_history"}],
            [{"text": "⬅ بازگشت", "callback_data": "back"}]
        ]
    }

# ---------------------
# شیت کاربر
# ---------------------
def get_user_sheet(chat_id):
    sheet_name = f"user_{chat_id}"
    try:
        sheet = gc.open(sheet_name)
    except gspread.SpreadsheetNotFound:
        sheet = gc.create(sheet_name)
        worksheet = sheet.sheet1
        worksheet.update("A1", [["تاریخ و زمان", "نوع علامت", "مقدار"]])
    return gc.open(sheet_name).sheet1

def add_symptom(chat_id, symptom_type, value):
    sheet = get_user_sheet(chat_id)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([now, symptom_type, value])

# ---------------------
# نمودار تاریخچه
# ---------------------
def generate_chart(chat_id):
    sheet = get_user_sheet(chat_id)
    data = sheet.get_all_records()
    if not data:
        return None

    sugar = [(row["تاریخ و زمان"], float(row["مقدار"])) for row in data if row["نوع علامت"] == "قند خون"]
    bp = [(row["تاریخ و زمان"], float(row["مقدار"])) for row in data if row["نوع علامت"] == "فشار خون"]
    weight = [(row["تاریخ و زمان"], float(row["مقدار"])) for row in data if row["نوع علامت"] == "وزن"]

    plt.figure(figsize=(10,5))

    if sugar:
        dates, values = zip(*sugar)
        plt.plot(dates, values, label="قند خون", marker='o')
    if bp:
        dates, values = zip(*bp)
        plt.plot(dates, values, label="فشار خون", marker='o')
    if weight:
        dates, values = zip(*weight)
        plt.plot(dates, values, label="وزن", marker='o')

    plt.xticks(rotation=45, ha="right")
    plt.ylabel("مقدار")
    plt.title("تاریخچه علائم")
    plt.legend()
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()
    return buf

def send_chart(chat_id, buf):
    url = BASE_URL + "sendPhoto"
    files = {"photo": buf}
    data = {"chat_id": chat_id}
    requests.post(url, data=data, files=files)
