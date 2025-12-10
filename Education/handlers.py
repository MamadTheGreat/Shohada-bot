import os
import requests

TOKEN = os.environ.get("BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"


def send_video(chat_id, video_path, caption=None):
    url = BASE_URL + "sendVideo"

    with open(video_path, "rb") as video:
        files = {"video": video}
        data = {"chat_id": chat_id}

        if caption:
            data["caption"] = caption

        requests.post(url, data=data, files=files)


def handle_education_callback(data, chat_id, send_message):
    if data == "edu":
        from .menus import disease_menu
        send_message(chat_id, "بیماری را انتخاب کنید:", disease_menu())

    elif data == "edu_diabetes":
        send_video(chat_id, "files/as.mp4", "آموزش دیابت نوع ۲")

    elif data == "edu_bp":
        send_video(chat_id, "files/aw.mp4", "آموزش فشار خون")

    elif data == "edu_heart":
        send_video(chat_id, "files/qw.mp4", "آموزش بیماری‌های قلبی")

    elif data == "back":
        from .menus import main_menu
        send_message(chat_id, "منوی اصلی :", main_menu())
