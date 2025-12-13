# Education.py

import os
import json
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
# ... (وارد کردن سایر کتابخانه‌های Drive API) ...
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --- توجه: MAIN_DRIVE_FOLDER_ID را حذف کرده و TOPIC_FOLDER_IDS را جایگزین می‌کنیم ---
from config import TOPIC_FOLDER_IDS, MAIN_MENU_BUTTONS, GDRIVE_CREDENTIALS_JSON, GDRIVE_TOKEN_JSON

# ... (بخش ۱: تنظیمات Google Drive و تابع get_drive_service بدون تغییر) ...

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"] 

def get_drive_service():
    """اعتبارنامه‌ها را از متغیرهای محیطی (Render) یا فایل (اجرای محلی) بارگذاری می‌کند."""
    # ... (کد get_drive_service اینجا بدون تغییر است) ...
    creds = None
    
    if GDRIVE_CREDENTIALS_JSON and GDRIVE_TOKEN_JSON:
        try:
            creds = Credentials.from_authorized_user_info(
                json.loads(GDRIVE_TOKEN_JSON), SCOPES
            )
        except Exception as e:
            print(f"Error loading creds from JSON: {e}")
            return None
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif os.path.exists("credentials.json"):
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        else:
            print("No valid credentials found.")
            return None

    try:
        service = build("drive", "v3", credentials=creds)
        return service
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

# --- تابع جدید برای دریافت فایل‌ها با استفاده از ID ثابت پوشه ---
def get_files_for_topic(topic_name: str):
    """
    فایل‌های موجود در پوشه مرتبط با موضوع درایو را با استفاده از ID ثابت پوشه پیدا می‌کند.
    """
    service = get_drive_service()
    
    # پیدا کردن ID پوشه از نگاشت
    topic_folder_id = TOPIC_FOLDER_IDS.get(topic_name)

    if not service or not topic_folder_id:
        # اگر سرویس آماده نیست یا ID پوشه در config.py پیدا نشد.
        return []

    try:
        # جستجو برای فایل‌های درون فولدر موضوع
        files_response = service.files().list(
            q=f"'{topic_folder_id}' in parents and trashed=false",
            fields="files(id, name, webContentLink)" # webContentLink برای لینک دانلود مستقیم
        ).execute()

        return files_response.get("files", [])

    except HttpError as error:
        print(f"An error occurred while searching files: {error}")
        return []

# --- ۲. تنظیمات منو و هندلرها (بدون تغییر) ---
LEARNING_MENU_BUTTONS = [
    [KeyboardButton("دیابت نوع ۲")],
    [KeyboardButton("فشار خون")],
    [KeyboardButton("بیماری قلبی عروقی")],
    [KeyboardButton("بازگشت به منوی اصلی")]
]

LEARNING_MENU_KEYBOARD = ReplyKeyboardMarkup(
    LEARNING_MENU_BUTTONS, 
    resize_keyboard=True, 
    one_time_keyboard=False
)

MAIN_MENU_KEYBOARD = ReplyKeyboardMarkup(
    MAIN_MENU_BUTTONS, 
    resize_keyboard=True, 
    one_time_keyboard=False
)

async def show_learning_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """نمایش منوی آموزش."""
    await update.message.reply_text(
        "📚 **بخش آموزش**\n\nلطفاً موضوع مورد نظر خود را انتخاب کنید:",
        reply_markup=LEARNING_MENU_KEYBOARD,
        parse_mode='Markdown'
    )

async def handle_learning_topic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """مدیریت انتخاب موضوعات آموزشی و ارسال فایل‌ها."""
    selected_topic = update.message.text
    
    if selected_topic == "بازگشت به منوی اصلی":
        await update.message.reply_text(
            "⬆️ **به منوی اصلی بازگشتید.**",
            reply_markup=MAIN_MENU_KEYBOARD,
            parse_mode='Markdown'
        )
        return

    # بررسی کنید آیا ID پوشه برای این موضوع تعریف شده است
    if selected_topic not in TOPIC_FOLDER_IDS:
        await update.message.reply_text(
            f"⚠️ ID پوشه برای **{selected_topic}** در تنظیمات تعریف نشده است.",
            reply_markup=LEARNING_MENU_KEYBOARD,
            parse_mode='Markdown'
        )
        return

    await update.message.reply_text(
        f"⏳ در حال جستجو و ارسال فایل‌های آموزشی برای **{selected_topic}**...",
        parse_mode='Markdown'
    )
    
    files = get_files_for_topic(selected_topic)

    if not files:
        await update.message.reply_text(
            f"❌ متأسفانه، هیچ فایل آموزشی برای **{selected_topic}** در پوشه گوگل درایو پیدا نشد. لطفاً دسترسی پوشه را چک کنید.",
            reply_markup=LEARNING_MENU_KEYBOARD,
            parse_mode='Markdown'
        )
        return

    # ارسال لینک فایل‌ها
    file_messages = [f"📥 **{file['name']}**:\n{file.get('webContentLink', 'لینک دانلود نامعتبر است.')}" for file in files]
    
    await update.message.reply_text(
        f"✅ {len(files)} فایل آموزشی پیدا شد:\n\n" + "\n---\n".join(file_messages),
        reply_markup=LEARNING_MENU_KEYBOARD,
        parse_mode='Markdown'
    )

# --- هندلرها برای Bot.py (بدون تغییر) ---
EDUCATION_ENTRY_HANDLER = MessageHandler(filters.Regex("^آموزش$"), show_learning_menu)
EDUCATION_TOPIC_HANDLER = MessageHandler(
    filters.Regex("^(دیابت نوع ۲|فشار خون|بیماری قلبی عروقی|بازگشت به منوی اصلی)$"), 
    handle_learning_topic
)

