# config.py

import os

# ... (تنظیمات تلگرام و توکن‌ها بدون تغییر) ...

# --- تنظیمات Google Drive ---
# نگاشت نام بیماری به ID پوشه مستقیم
# توجه: ID اصلی پوشه (MAIN_DRIVE_FOLDER_ID) دیگر لازم نیست.
TOPIC_FOLDER_IDS = {
    "دیابت نوع ۲": "1zbYAAm6DXVl5IZqH_mw88Ny_-RBShpdT",
    "فشار خون": "1iMuAXupOZFopDdgrFEDwvpr8IynelIFp",
    "بیماری قلبی عروقی": "YOUR_CARDIO_FOLDER_ID_HERE" # این مورد باید توسط شما اضافه شود
}

# اعتبارنامه‌ها و توکن‌ها برای اجرای در Render (بدون تغییر)
GDRIVE_CREDENTIALS_JSON = os.environ.get("GDRIVE_CREDENTIALS_JSON")
GDRIVE_TOKEN_JSON = os.environ.get("GDRIVE_TOKEN_JSON")

# ... (دکمه‌های اصلی بدون تغییر) ...
