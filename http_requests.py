import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import matplotlib.pyplot as plt

# مسیر فایل سرویس اکانت گوگل
creds_path = os.path.join("config", "google_sa.json")

# دسترسی به Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
client = gspread.authorize(creds)

# نام پیش‌فرض شیت
DEFAULT_SHEET_NAME = "ShohadaBot"

def get_user_sheet(user_id):
    """شیت مخصوص کاربر را باز می‌کند یا ایجاد می‌کند"""
    try:
        sh = client.open(str(user_id))
    except gspread.SpreadsheetNotFound:
        sh = client.create(str(user_id))
        # اضافه کردن شیت اولیه
        worksheet = sh.sheet1
        worksheet.update("A1", [["تاریخ و ساعت", "قند خون", "فشار خون", "وزن"]])
    return sh.sheet1

def add_symptom(user_id, blood_sugar=None, bp=None, weight=None):
    """ثبت یک رکورد جدید در شیت کاربر"""
    sheet = get_user_sheet(user_id)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [now, blood_sugar, bp, weight]
    sheet.append_row(row)

def get_symptoms_history(user_id):
    """خواندن تمام رکوردها"""
    sheet = get_user_sheet(user_id)
    records = sheet.get_all_records()
    return records

def plot_symptoms(user_id):
    """نمودار علائم را بر اساس تاریخ رسم می‌کند"""
    history = get_symptoms_history(user_id)
    if not history:
        return None

    dates = [datetime.datetime.strptime(r["تاریخ و ساعت"], "%Y-%m-%d %H:%M:%S") for r in history]
    sugar = [r["قند خون"] if r["قند خون"] else None for r in history]
    bp = [r["فشار خون"] if r["فشار خون"] else None for r in history]
    weight = [r["وزن"] if r["وزن"] else None for r in history]

    plt.figure(figsize=(8,5))
    if any(sugar):
        plt.plot(dates, sugar, marker='o', label="قند خون")
    if any(bp):
        plt.plot(dates, bp, marker='x', label="فشار خون")
    if any(weight):
        plt.plot(dates, weight, marker='s', label="وزن")

    plt.xlabel("تاریخ و ساعت")
    plt.ylabel("مقدار")
    plt.title("تاریخچه علائم")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    img_path = os.path.join("files", f"{user_id}_history.png")
    plt.savefig(img_path)
    plt.close()
    return img_path
