import os
from http_requests import telegram_post
import json

def send_message(chat_id, text, reply_markup=None):
    data = {"chat_id": chat_id, "text": text}
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup, ensure_ascii=False)
    telegram_post("sendMessage", data)

def send_video(chat_id, video_key):
    mapping = {
        "edu_diabetes": ("files/as.mp4", "آموزش دیابت نوع ۲"),
        "edu_bp": ("files/aw.mp4", "آموزش فشار خون"),
        "edu_heart": ("files/qw.mp4", "آموزش بیماری‌های قلبی")
    }
    if video_key not in mapping:
        return
    path, caption = mapping[video_key]
    if not os.path.exists(path):
        print(f"Video not found: {path}")
        return
    with open(path, "rb") as f:
        files = {"video": f}
        data = {"chat_id": chat_id, "caption": caption}
        telegram_post("sendVideo", data, files)

def main_menu():
    return {
        "inline_keyboard": [
            [{"text": "📘 آموزش بیماری‌ها", "callback_data": "edu"}],
            [{"text": "📝 ثبت علائم", "callback_data": "symptoms"}],
            [{"text": "👤 اتصال به کارشناس", "callback_data": "expert"}]
        ]
    }

def disease_menu():
    return {
        "inline_keyboard": [
            [{"text": "دیابت نوع ۲", "callback_data": "edu_diabetes"}],
            [{"text": "فشار خون", "callback_data": "edu_bp"}],
            [{"text": "بیماری‌های قلبی", "callback_data": "edu_heart"}],
            [{"text": "⬅ بازگشت", "callback_data": "back"}]
        ]
    }
