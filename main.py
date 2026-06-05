from fastapi import FastAPI, Request
import requests
import os

app = FastAPI()

VERIFY_TOKEN = "amer123"
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

@app.get("/")
def home():
    return {"status": "working"}


@app.get("/webhook")
async def verify_webhook(request: Request):

    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return str(challenge)

    return {"error": "Invalid token"}


@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()
    print("NEW REQUEST")
    print(data)

    try:
        event = data["entry"][0]["messaging"][0]

        if "message" not in event:
            return {"status": "ignored"}

        message_text = event["message"].get("text", "").lower()
        sender_id = event["sender"]["id"]
        print("MESSAGE TEXT =", message_text)
        print("SENDER ID =", sender_id)

        if "سخان وسط" in message_text:
            reply = """🍪 سخان كيكة كوكيز وسط

👥 يكفي 5–7 أشخاص

💰 السعر: 15000 د.ع

📞📍 للتثبيت يرجى إرسال رقم الهاتف والعنوان."""

        elif "سخان صغير" in message_text:
            reply = """🍪 سخان كيكة كوكيز صغيرة

👥 يكفي 3–4 أشخاص

💰 السعر: 8000 د.ع

📞📍 للتثبيت يرجى إرسال رقم الهاتف والعنوان."""

        elif "سخان كبير" in message_text:
            reply = """🍪 سخان كيكة كوكيز كبيرة

👥 يكفي 8–11 شخص

💰 السعر: 25000 د.ع

📞📍 للتثبيت يرجى إرسال رقم الهاتف والعنوان."""

        elif "فردي" in message_text:
            reply = """🍪 سخان كيكة كوكيز فردي

👤 يكفي شخص واحد

💰 السعر: 2500 د.ع

📞📍 للتثبيت يرجى إرسال رقم الهاتف والعنوان."""

        elif (
            "التوصيل" in message_text
            or "سعر التوصيل" in message_text
            or "شكد التوصيل" in message_text
            or "اجور التوصيل" in message_text
        ):
            reply = """🚚 عرض التوصيل حالياً 2000 دينار فقط ❤️

يشمل جميع مناطق كربلاء 🌹"""

        elif any(char.isdigit() for char in message_text):
            reply = """✅ تم تثبيت طلبكم بنجاح ❤️🍪

🚚 سيتم التوصيل خلال ساعتين من تأكيد الحجز."""
telegram_message = f"""
📦 طلب جديد من الانستكرام

👤 User ID: {sender_id}

📱 الرقم المرسل:
{message_text}
"""

requests.post(
    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
    json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": telegram_message
    }
)
        else:
            reply = """هلا وغلا ❤️🍪

🍪 سخان كيكة كوكيز
🥐 كرواسون محشي
🍩 دونات
🍹 مشروبات

راسلنا باسم المنتج المطلوب وسنزودك بالسعر مباشرة."""

        r = requests.post(
            f"https://graph.instagram.com/v23.0/me/messages?access_token={INSTAGRAM_ACCESS_TOKEN}",
            json={
                "recipient": {"id": sender_id},
                "message": {"text": reply}
            }
        )
        print("META STATUS =", r.status_code)
        print("TOKEN =", INSTAGRAM_ACCESS_TOKEN)
        print("META RESPONSE =", r.text)

    except Exception as e:
        print("ERROR:", e)

    return {"status": "ok"}
