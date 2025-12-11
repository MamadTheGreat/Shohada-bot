import os
import json
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from googleapiclient.discovery import build
from google.oauth2 import service_account

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Google Sheets creds و Sheet ID از ENV
google_sa = json.loads(os.environ["GOOGLE_CREDS"])
SHEET_ID = os.environ["SHEET_ID"]

creds = service_account.Credentials.from_service_account_info(google_sa, scopes=SCOPES)
service = build("sheets", "v4", credentials=creds)
sheet = service.spreadsheets().values()

RANGE = "Symptoms!A:E"  # ستون‌ها: Date | Glucose | Sys | Dia | Weight

def add_symptom(user_id, symptom_type, value):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    glucose = sys_bp = dia_bp = weight = ""
    if symptom_type == "قند خون":
        glucose = value
    elif symptom_type == "فشار خون":
        sys_bp = value
    elif symptom_type == "وزن":
        weight = value

    row = [timestamp, glucose, sys_bp, dia_bp, weight]
    try:
        sheet.append(spreadsheetId=SHEET_ID, range=RANGE,
                     valueInputOption="USER_ENTERED", body={"values": [row]}).execute()
    except Exception as e:
        print("Error saving symptom:", e)

def get_symptom_history(symptom_type):
    try:
        data = sheet.get(spreadsheetId=SHEET_ID, range=RANGE).execute()
        values = data.get("values", [])
    except Exception as e:
        print("Error loading sheet:", e)
        return None

    if len(values) <= 1:
        return None

    df = pd.DataFrame(values[1:], columns=values[0])

    if symptom_type == "قند خون":
        df = df[df["Glucose"] != ""]
        df["Glucose"] = df["Glucose"].astype(float)
    elif symptom_type == "فشار خون":
        df = df[df["Sys"] != ""]
        df["Sys"] = df["Sys"].astype(float)
        df["Dia"] = df["Dia"].astype(float)
    elif symptom_type == "وزن":
        df = df[df["Weight"] != ""]
        df["Weight"] = df["Weight"].astype(float)
    else:
        return None
    return df

def plot_symptoms(user_id):
    os.makedirs("files", exist_ok=True)
    final_path = os.path.join("files", f"{user_id}_history.png")

    df_glucose = get_symptom_history("قند خون")
    df_bp = get_symptom_history("فشار خون")
    df_weight = get_symptom_history("وزن")

    if all(x is None or x.empty for x in [df_glucose, df_bp, df_weight]):
        return None

    plt.figure(figsize=(10,5))
    if df_glucose is not None and not df_glucose.empty:
        plt.plot(df_glucose["Date"], df_glucose["Glucose"], marker="o", label="قند خون")
    if df_bp is not None and not df_bp.empty:
        plt.plot(df_bp["Date"], df_bp["Sys"], marker="x", label="فشار خون سیستول")
        plt.plot(df_bp["Date"], df_bp["Dia"], marker=".", label="فشار خون دیاستول")
    if df_weight is not None and not df_weight.empty:
        plt.plot(df_weight["Date"], df_weight["Weight"], marker="s", label="وزن")

    plt.xlabel("تاریخ و ساعت")
    plt.ylabel("مقدار")
    plt.title("تاریخچه علائم")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(final_path)
    plt.close()

    return final_path
