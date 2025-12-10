import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import matplotlib.pyplot as plt
import requests

# مسیر فایل JSON سرویس اکانت گوگل
creds_path = "config/google_service_account.json"
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
client = gspread.authorize(creds)

# منوی علائم
def symptoms_menu():
    return {
        "inline_keyboard": [
            [{"text": "قند خون", "callback_data": "sym_blood"}],
            [{"text": "فشار خون", "callback_data": "sym_bp"}],
            [{"text": "وزن", "callback_data": "sym_weight"}],
            [{"text": "مشاهده تاریخچه علائم", "callback_data": "sym_history"}],
            [{"text": "⬅ بازگشت", "callback_data": "back"}]
        ]
    }

# ثبت مقدار در شیت
def handle_symptom_input(chat_id, value, user_state):
    sheet_name = f"user_{chat_id}"
    try:
        sheet = client.open(sheet_name).sheet1
    except:
        sheet = client.create(sheet_name).sheet1
        sheet.append_row(["timestamp", "type", "value"])

    current_type = user_state[chat_id]["expecting"]
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([timestamp, current_type, value])
    user_state.pop(chat_id, None)

# نمایش نمودار تاریخچه
def show_history(chat_id):
    sheet_name = f"user_{chat_id}"
    try:
        sheet = client.open(sheet_name).sheet1
    except:
        return

    records = sheet.get_all_records()
    if not records:
        return

    types = list(set([r["type"] for r in records]))
    for t in types:
        data = [float(r["value"]) for r in records if r["type"] == t]
        times = [r["timestamp"] for r in records if r["type"] == t]
        plt.plot(times, data, label=t)

    plt.xlabel("زمان")
    plt.ylabel("مقدار")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    img_path = f"files/{chat_id}_history.png"
    plt.savefig(img_path)
    plt.close()

    url = f"https://api.telegram.org/bot{os.environ.get('BOT_TOKEN')}/sendPhoto"
    files = {"photo": open(img_path, "rb")}
    data = {"chat_id": chat_id}
    requests.post(url, data=data, files=files)
