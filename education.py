import http_requests, json, os

TOKEN = os.environ.get("BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

def send_message(chat_id, text, reply_markup=None):
    url = BASE_URL + "sendMessage"
    data = {"chat_id": chat_id, "text": text}
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    http_requests.post(url, data=data)

def send_video(chat_id, video_data):
    mapping = {
        "edu_diabetes": ("files/as.mp4", "آموزش دیابت نوع ۲"),
        "edu_bp": ("files/aw.mp4", "آموزش فشار خون"),
        "edu_heart": ("files/qw.mp4", "آموزش بیماری‌های قلبی")
    }
    if video_data not in mapping:
        return
    path, caption = mapping[video_data]
    url = BASE_URL + "sendVideo"
    files = {"video": open(path, "rb")}
    data = {"chat_id": chat_id, "caption": caption}
    http_requests.post(url, data=data, files=files)

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
