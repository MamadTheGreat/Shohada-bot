import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import os
import matplotlib.pyplot as plt

# ===== تنظیم مسیر فایل JSON سرویس اکانت =====
CREDS_PATH = os.path.join("config", "google_sa.json")

# ===== اتصال به Google Sheet =====
def get_client():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_PATH, scope)
    return gspread.authorize(creds)

# ===== پیدا کردن یا ساخت شیت مخصوص هر کاربر =====
def get_or_create_sheet(chat_id):
    client = get_client()
    sheet_name = f"user_{chat_id}_symptoms"

    try:
        sheet = client.open(sheet_name).sheet1
    except:
        sheet = client.create(sheet_name).sheet1
        # هدرها
        sheet.append_row(["date", "time", "type", "value"])

    return sheet

# ===== افزودن علامت =====
def add_symptom(chat_id, symptom_type, value):
    sheet = get_or_create_sheet(chat_id)
    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    sheet.append_row([date, time, symptom_type, value])

# ===== ساخت نمودار =====
def plot_symptoms(chat_id):
    sheet = get_or_create_sheet(chat_id)
    rows = sheet.get_all_values()

    # اگر فقط هدر وجود دارد
    if len(rows) <= 1:
        return None

    dates = []
    values = []

    for row in rows[1:]:
        try:
            date_time = f"{row[0]} {row[1]}"
            value = float(row[3])
            dates.append(date_time)
            values.append(value)
        except:
            continue

    if not values:
        return None

    plt.figure()
    plt.plot(dates, values, marker="o")
    plt.xticks(rotation=45)
    plt.tight_layout()

    img_path = f"symptoms_{chat_id}.png"
    plt.savefig(img_path)
    plt.close()

    return img_path
