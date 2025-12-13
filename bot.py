# Bot.py

import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import TELEGRAM_BOT_TOKEN, PORT, WEBHOOK_URL, MAIN_MENU_BUTTONS
from Education import EDUCATION_ENTRY_HANDLER, EDUCATION_TOPIC_HANDLER
from Symptoms import SYMPTOM_ENTRY_HANDLER

# --- تنظیمات لاگینگ ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ساختار کیبورد منوی اصلی (تعریف مجدد برای این ماژول)
MAIN_MENU_KEYBOARD = ReplyKeyboardMarkup(
    MAIN_MENU_BUTTONS, 
    resize_keyboard=True, 
    one_time_keyboard=False
)

# --- هندلر فرمان /start و خوش آمدگویی ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ارسال پیام خوش آمد و نمایش منوی اصلی."""
    await update.message.reply_text(
        "👋 **به ربات سلامتی و آموزش خوش آمدید!**\n\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=MAIN_MENU_KEYBOARD,
        parse_mode='Markdown'
    )

# --- هندلر 'ارتباط با کارشناس' ---
async def contact_expert(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """مدیریت دکمه 'ارتباط با کارشناس'."""
    await update.message.reply_text(
        "📞 **ارتباط با کارشناس**\n\nلطفاً پیام خود را برای کارشناس ارسال کنید. "
        "کارشناسان ما در اسرع وقت پاسخ خواهند داد.",
        reply_markup=MAIN_MENU_KEYBOARD,
        parse_mode='Markdown'
    )

def main() -> None:
    """شروع به کار ربات و مدیریت Webhook/Polling."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # --- اضافه کردن هندلرها ---
    
    # 1. Start Command و منوی اصلی
    application.add_handler(CommandHandler("start", start_command))
    
    # 2. ماژول Education (ورود به منو و مدیریت موضوعات)
    application.add_handler(EDUCATION_ENTRY_HANDLER)
    application.add_handler(EDUCATION_TOPIC_HANDLER)
    
    # 3. ماژول Symptoms
    application.add_handler(SYMPTOM_ENTRY_HANDLER)
    
    # 4. ارتباط با کارشناس
    application.add_handler(MessageHandler(filters.Regex("^ارتباط با کارشناس$"), contact_expert))
    
    # --- اجرای ربات با Webhook یا Polling ---
    if WEBHOOK_URL:
        # اجرای Webhook (برای Render)
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TELEGRAM_BOT_TOKEN,
            webhook_url=f"{WEBHOOK_URL}{TELEGRAM_BOT_TOKEN}"
        )
        logger.info(f"ربات در حال اجرا با Webhook در پورت {PORT} و URL: {WEBHOOK_URL}")
    else:
        # اجرای Polling (برای توسعه محلی)
        logger.info("ربات در حال اجرا با Polling (محلی)")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
