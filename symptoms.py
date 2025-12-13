import os
import json
import matplotlib.pyplot as plt
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

SERVICE_ACCOUNT_INFO = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT"])

creds = service_account.Credentials.from_service_account_info(
    SERVICE_ACCOUNT_INFO,
    scopes=SCOPES
)

service = build("sheets", "v4", credentials=creds)

SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")

def add_symptom(user_id, symptom, value):
    body = {
        "values": [[str(user_id), symptom, value]]
    }
    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range="Sheet1!A:C",
        valueInputOption="RAW",
        body=body
    ).execute()

def plot_symptoms(user_id):
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="Sheet1!A:C"
    ).execute()

    rows = result.get("values", [])
    sugars = [float(r[2]) for r in rows if r[0] == str(user_id) and r[1] == "sugar"]

    if not sugars:
        return None

    plt.figure()
    plt.plot(sugars)
    plt.title("روند قند خون")
    plt.xlabel("دفعات ثبت")
    plt.ylabel("mg/dl")

    path = f"/tmp/{user_id}_sugar.png"
    plt.savefig(path)
    plt.close()

    return path
