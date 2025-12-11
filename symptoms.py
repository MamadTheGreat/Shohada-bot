import os
import json
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # جلوگیری از خطای گرافیکی در سرور
import matplotlib.pyplot as plt
import pandas as pd
from googleapiclient.discovery import build
from google.oauth2 import service_account

# تنظیمات گوگل شیت
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SHEET_ID = os.environ.get("SHEET_ID")
RANGE = "Symptoms!A:E"

def get_google_service():
    """اتصال به گوگل شیت با فایل یا متغیر محیطی"""
    creds = None
    try:
        # روش اول: خواندن از متغیر محیطی (برای هاست واقعی)
        google_creds_json = os.environ.get("GOOGLE_CREDENTIALS")
        if google_creds_json:
            creds_info = json.loads(google_creds_json)
            creds = service_account.Credentials.from_service_account_info(creds_info, scopes=SCOPES)
        # روش دوم: خواندن از فایل (برای تست روی کامپیوتر خودتان)
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
    # مقادیر پیش‌فرض خالی
    glucose = sys_bp = dia_bp = weight = ""
    
    # تطبیق نوع ورودی
    if "قند" in symptom_type:
        glucose = value
    elif "فشار" in symptom_type:
        sys_bp = value # فرض ساده: فقط یک عدد می‌گیریم
    elif "وزن" in symptom_type:
        weight = value
    else:
        # ذخیره سایر موارد به عنوان توضیحات یا ... (فعلا نادیده می‌گیریم)
        pass

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
        data = sheet.get(spreadsheetId=SHEET_ID, range=RANGE).execute()
        values = data.get("values", [])
    except Exception as e:
        print("Error reading sheet:", e)
        return None

    if len(values) <= 1:
        return None

    # فرض می‌کنیم ستون‌ها به ترتیب: تاریخ، یوزرآیدی، قند، فشار، وزن هستند
    # اگر هدر فایل شیت شما فرق دارد، اینجا را تغییر دهید
    df = pd.DataFrame(values[1:], columns=["Date", "UserID", "Glucose", "BP", "Weight"])
    
    # فیلتر کردن بر اساس کاربر فعلی
    df = df[df["UserID"] == str(user_id)]
    
    if df.empty:
        return None
        
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df

def plot_symptoms(user_id):
    df = get_symptom_history(user_id)
    if df is None or df.empty:
        return None

    os.makedirs("files", exist_ok=True)
    final_path = os.path.join("files", f"{user_id}_history.png")

    plt.figure(figsize=(8, 5))

    # تبدیل ستون‌ها به عدد برای رسم نمودار
    has_data = False
    
    # رسم قند خون
    if "Glucose" in df.columns:
        df["Glucose"] = pd.to_numeric(df["Glucose"], errors='coerce')
        if df["Glucose"].notna().any():
            plt.plot(df["Date"], df["Glucose"], marker="o", label="قند خون", color="red")
            has_data = True

    # رسم وزن
    if "Weight" in df.columns:
        df["Weight"] = pd.to_numeric(df["Weight"], errors='coerce')
        if df["Weight"].notna().any():
            plt.plot(df["Date"], df["Weight"], marker="s", label="وزن", color="blue")
            has_data = True
            
    # رسم فشار
    if "BP" in df.columns:
        df["BP"] = pd.to_numeric(df["BP"], errors='coerce')
        if df["BP"].notna().any():
            plt.plot(df["Date"], df["BP"], marker="^", label="فشار خون", color="green")
            has_data = True

    if not has_data:
        plt.close()
        return None

    plt.title(f"نمودار سلامت کاربر {user_id}")
    plt.xlabel("زمان")
    plt.ylabel("مقدار")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    plt.savefig(final_path)
    plt.close() # بستن پلات برای آزاد شدن رم
    return final_path
