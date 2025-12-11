import os
import json
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # مهم: برای جلوگیری از خطای گرافیکی در سرور
import matplotlib.pyplot as plt
import pandas as pd
from googleapiclient.discovery import build
from google.oauth2 import service_account

# --- تنظیمات گوگل شیت ---
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SHEET_ID = os.environ.get("SHEET_ID")
RANGE = "Symptoms!A:E"

def get_google_service():
    """اتصال به گوگل شیت با متغیر محیطی (امن‌ترین روش برای Render)"""
    creds = None
    try:
        # روش اول: خواندن از متغیر محیطی (برای هاستینگ)
        google_creds_json = os.environ.get("GOOGLE_CREDENTIALS")
        if google_creds_json:
            creds_info = json.loads(google_creds_json)
            creds = service_account.Credentials.from_service_account_info(creds_info, scopes=SCOPES)
        # روش دوم: خواندن از فایل (برای توسعه محلی)
        elif os.path.exists("service_account.json"):
            creds = service_account.Credentials.from_service_account_file("service_account.json", scopes=SCOPES)
        else:
            print("No Google Credentials found!")
            return None
            
        service = build("sheets", "v4", credentials=creds)
        return service.spreadsheets().values()
    except Exception as e:
        print(f"Google Auth Error: {e}")
        return None

def add_symptom(user_id, symptom_type, value):
    sheet = get_google_service()
    if not sheet:
        return False

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # مقادیر ستون‌های شیت (تاریخ, یوزرآیدی, قند, فشار سیستول, وزن)
    glucose = sys_bp = weight = ""
    
    # تطبیق نوع ورودی
    if "قند" in symptom_type or "گلوکز" in symptom_type:
        glucose = value
    elif "فشار" in symptom_type:
        # اگر کاربر فقط یک عدد داد، فرض می‌کنیم فشار سیستول است
        sys_bp = value 
    elif "وزن" in symptom_type:
        weight = value
    else:
        # اگر نوع علائم تعریف نشده باشد، ثبت نمی‌شود.
        return False

    row = [timestamp, str(user_id), glucose, sys_bp, weight]
    
    try:
        sheet.append(
            spreadsheetId=SHEET_ID, range=RANGE,
            valueInputOption="USER_ENTERED", body={"values": [row]}
        ).execute()
        return True
    except Exception as e:
        print("Error saving to sheet:", e)
        return False

def get_symptom_history(user_id):
    sheet = get_google_service()
    if not sheet:
        return None

    try:
        # دریافت کل داده‌ها
        data = sheet.get(spreadsheetId=SHEET_ID, range=RANGE).execute()
        values = data.get("values", [])
    except Exception as e:
        print("Error reading sheet:", e)
        return None

    if len(values) <= 1:
        return None

    # ساخت DataFrame (فرض می‌کنیم ستون‌ها به ترتیب: Date, UserID, Glucose, BP, Weight)
    df = pd.DataFrame(values[1:], columns=["Date", "UserID", "Glucose", "BP", "Weight"])
    
    # فیلتر کردن بر اساس کاربر فعلی
    df = df[df["UserID"] == str(user_id)].copy()
    
    if df.empty:
        return None
        
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    
    # تبدیل ستون‌ها به عدد
    for col in ["Glucose", "BP", "Weight"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    # حذف ردیف‌هایی که هیچ داده عددی ندارند
    df = df.dropna(subset=["Glucose", "BP", "Weight"], how='all')
    
    return df.sort_values(by="Date")

def plot_symptoms(user_id):
    df = get_symptom_history(user_id)
    if df is None or df.empty:
        return None

    os.makedirs("files", exist_ok=True)
    final_path = os.path.join("files", f"{user_id}_history.png")

    plt.figure(figsize=(10, 6))

    has_data = False
    
    # رسم قند خون
    if df["Glucose"].notna().any():
        plt.plot(df["Date"], df["Glucose"], marker="o", label="قند خون (Glucose)", color="red")
        has_data = True

    # رسم فشار
    if df["BP"].notna().any():
        plt.plot(df["Date"], df["BP"], marker="^", label="فشار خون سیستول (Systolic BP)", color="green")
        has_data = True

    # رسم وزن
    if df["Weight"].notna().any():
        plt.plot(df["Date"], df["Weight"], marker="s", label="وزن (Weight)", color="blue")
        has_data = True

    if not has_data:
        plt.close()
        return None

    plt.title(f"نمودار سلامت کاربر {user_id}", fontsize=14)
    plt.xlabel("زمان", fontsize=12)
    plt.ylabel("مقدار", fontsize=12)
    plt.legend(loc='best', fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    try:
        plt.savefig(final_path)
        plt.close()
        return final_path
    except Exception as e:
        print(f"Error saving chart: {e}")
        plt.close()
        return None

