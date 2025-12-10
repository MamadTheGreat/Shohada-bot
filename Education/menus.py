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
