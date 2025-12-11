import os
import json
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO

from googleapiclient.discovery import build
from google.oauth2 import service_account

# ===== Google Sheets Config =====
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# از ENV در Render خوانده می‌شود
google_sa = json.loads(os.environ["GOOGLE_CREDS"])
SHEET_ID = os.environ["SHEET_ID"]

creds = service_account.Credentials.from_service_account_info(
    google_sa, scopes=SCOPES
)

service = build("sheets", "v4", credentials=creds)
sheet = service.spreadsheets().values()

RANGE = "Symptoms!A:F"


# -----------------------------
# ثبت علائم
# -----------------------------
def save_symptoms(user_id, glucose="", sys_bp="", dia_bp="", weight="", other=""):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    row = [timestamp, glucose, sys_bp, dia_bp, weight, other]

    sheet.append(
        spreadsheetId=SHEET_ID,
        range=RANGE,
        valueInputOption="USER_ENTERED",
        body={"values": [row]},
    ).execute()


# -----------------------------
# استخراج تاریخچه
# -----------------------------
def load_history(symptom_type):
    data = sheet.get(
        spreadsheetId=SHEET_ID,
        range=RANGE
    ).execute()

    values = data.get("values", [])

    if len(values) <= 1:
        return None

    df = pd.DataFrame(values[1:], columns=values[0])

    if symptom_type == "glucose":
        df = df[df["Glucose"] != ""]
        df["Glucose"] = df["Glucose"].astype(float)
        return df

    if symptom_type == "bp":
        df = df[df["Sys"] != ""]
        df["Sys"] = df["Sys"].astype(float)
        df["Dia"] = df["Dia"].astype(float)
        return df

    if symptom_type == "weight":
        df = df[df["Weight"] != ""]
        df["Weight"] = df["Weight"].astype(float)
        return df

    return None


# -----------------------------
# ساخت نمودار و ارسال عکس
# -----------------------------
def build_plot(df, symptom):
    fig, ax = plt.subplots(figsize=(7, 4))

    if symptom == "glucose":
        ax.plot(df["Date"], df["Glucose"])
        ax.set_title("تاریخچه قند خون")
        ax.set_ylabel("mg/dL")

    elif symptom == "bp":
        ax.plot(df["Date"], df["Sys"], label="سیستول")
        ax.plot(df["Date"], df["Dia"], label="دیاستول")
        ax.set_title("تاریخچه فشار خون")
        ax.legend()

    elif symptom == "weight":
        ax.plot(df["Date"], df["Weight"])
        ax.set_title("تاریخچه وزن")

    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()

    return buf