from fastapi import FastAPI, Request
import requests
import os

app = FastAPI()

VERIFY_TOKEN = "amer123"
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")


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

    try:
        event = data["entry"][0]["messaging"][0]

        if "message" not in event:
            return {"status": "ignored"}

        message_text = event["message"].get("text", "").lower()
        sender_id = event["sender"]["id"]

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

        else:
            reply = """هلا وغلا ❤️🍪

🍪 سخان كيكة كوكيز
🥐 كرواسون محشي
🍩 دونات
🍹 مشروبات

راسلنا باسم المنتج المطلوب وسنزودك بالسعر مباشرة."""

        requests.post(
            f"https://graph.facebook.com/v23.0/me/messages?access_token={INSTAGRAM_ACCESS_TOKEN}",
            json={
                "recipient": {"id": sender_id},
                "message": {"text": reply}
            }
        )

    except Exception as e:
        print("ERROR:", e)

    return {"status": "ok"}


import uvicorn

if name == "main":
    uvicorn.run(app, host="0.0.0.0", port=8000)
