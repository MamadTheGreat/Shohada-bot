import os
import json
from flask import Flask, request
from education import send_video, main_menu, disease_menu
from symptoms import add_symptom, plot_symptoms
from http_requests import telegram_post

# --------- Flask App ---------
app = Flask(__name__)

# وضعیت کاربران (در صورت ری‌استارت، از فایل JSON خوانده می‌شود)
STATE_FILE = "user_state.json"
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        user_state = json.load(f)
else:
    user_state = {}

def save_user_state():
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(user_state, f, ensure_ascii=False)

# --------- ارسال پیام و عکس ---------
def send_message(chat_id, text, reply_markup=None):
    data = {"chat_id": chat_id, "text": text}
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup, ensure_ascii=False)
    telegram_post("sendMessage", data)

def send_photo(chat_id, photo_path, caption=None):
    data = {"chat_id": chat_id}
    if caption:
        data["caption"] = caption
    telegram_post("sendPhoto", data, files={"photo": open(photo_path, "rb")})

# --------- Webhook ---------
@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()

    # ---------- پیام متنی ----------
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")

        # اگر کاربر در حالت ثبت علامت باشد
        if str(chat_id) in user_state:
            symptom_type = user_state.pop(str(chat_id))
            save_user_state()
            try:
                value = float(text)
                add_symptom(chat_id, symptom_type, value)
                send_message(chat_id, f"{symptom_type} شما با مقدار {value} ثبت شد.")
            except ValueError:
                send_message(chat_id, "لطفاً یک عدد معتبر وارد کنید.")

        elif text == "/start":
            send_message(chat_id, "به ربات آموزشی بیمارستان شهدا خوش آمدید.", main_menu())

    # ---------- callback_query ----------
    if "callback_query" in update:
        cq = update["callback_query"]
        chat_id = cq["message"]["chat"]["id"]
        data = cq["data"]

        # ---- آموزش ----
        if data == "edu":
            send_message(chat_id, "بیماری را انتخاب کنید:", disease_menu())
        elif data in ["edu_diabetes", "edu_bp", "edu_heart"]:
            send_video(chat_id, data)

        # ---- ثبت علائم ----
        elif data == "symptoms":
            reply = {
                "inline_keyboard": [
                    [{"text": "قند خون", "callback_data": "symp_sugar"}],
                    [{"text": "فشار خون", "callback_data": "symp_bp"}],
                    [{"text": "وزن", "callback_data": "symp_weight"}],
                    [{"text": "📊 مشاهده تاریخچه علائم", "callback_data": "symp_history"}],
                    [{"text": "⬅ بازگشت", "callback_data": "back"}]
                ]
            }
            send_message(chat_id, "علائم را انتخاب کنید:", reply)

        elif data == "symp_history":
            img_path = plot_symptoms(chat_id)
            if img_path:
                send_photo(chat_id, img_path, "تاریخچه علائم شما")
            else:
                send_message(chat_id, "هیچ رکوردی برای شما ثبت نشده است.")

        elif data in ["symp_sugar", "symp_bp", "symp_weight"]:
            symptom_map = {
                "symp_sugar": "قند خون",
                "symp_bp": "فشار خون",
                "symp_weight": "وزن"
            }
            user_state[str(chat_id)] = symptom_map[data]
            save_user_state()
            send_message(chat_id, f"لطفاً مقدار {symptom_map[data]} خود را وارد کنید:")

        # ---- اتصال به کارشناس ----
        elif data == "expert":
            send_message(chat_id,
                         "برای ارتباط با کارشناس لطفاً پیام خود را ارسال کنید.\n"
                         "کارشناس در کمتر از ۲۴ ساعت پاسخ می‌دهد.")

        # ---- بازگشت به منوی اصلی ----
        elif data == "back":
            send_message(chat_id, "منوی اصلی :", main_menu())

    return "ok"

@app.route("/")
def home():
    return "Bot is running"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
