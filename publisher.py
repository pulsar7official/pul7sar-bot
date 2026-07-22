import os
import requests

def send_to_telegram(image_path, caption_text):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        print("⚠️ لم يتم العثور على مفاتيح Telegram. يتم تخطي النشر.")
        return False

    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"

    try:
        with open(image_path, "rb") as photo_file:
            payload = {
                "chat_id": chat_id,
                "caption": caption_text,
                "parse_mode": "Markdown"
            }
            files = {"photo": photo_file}
            
            response = requests.post(url, data=payload, files=files, timeout=20)
            if response.status_code == 200:
                print("🚀 تم النشر بنجاح على منصة Telegram!")
                return True
            else:
                print(f"❌ خطأ أثناء النشر: {response.status_code} - {response.text}")
                return False
    except Exception as e:
        print(f"⚠️ خطأ أثناء الاتصال بـ Telegram: {e}")
        return False
