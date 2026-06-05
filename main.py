from fastapi import FastAPI, Request
import requests
import os

app = FastAPI()
user_orders = {}
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
            user_orders[sender_id] = "سخان وسط"
            reply = """
        👥 يكفي 5–7 أشخاص
        
        💰 السعر: 15000 د.ع

📞📍 للتثبيت يرجى إرسال رقم الهاتف والعنوان."""

        elif "سخان صغير" in message_text:
            user_orders[sender_id] = "سخان صغير"
            reply = """
        👥 يكفي 3–4 أشخاص

💰 السعر: 8000 د.ع

📞📍 للتثبيت يرجى إرسال رقم الهاتف والعنوان."""

        elif "سخان كبير" in message_text:
            user_orders[sender_id] = "سخان كبير"
            reply = """
        👥 يكفي 8–11 شخص
        
        💰 السعر: 25000 د.ع

📞📍 للتثبيت يرجى إرسال رقم الهاتف والعنوان."""

        elif "فردي" in message_text:
            user_orders[sender_id] = "فردي"
            reply = """
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

🚚 سيتم التوصيل خلال ساعتين من تأكيد الحجز"""
     
               product = user_orders.get(sender_id, "منتج غير محدد")

telegram_message = f"""
📦 طلب جديد من الانستكرام

🍪 المنتج:
{product}

👤 User ID:
{sender_id}

📱 الرقم والعنوان:
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

نورتوا كوكيز لارين 🤤🔥

🍪 - سخان كيكة كوكيز -
• فردي (شخص) — 2,500 د.ع
• صغيرة (3–4 أشخاص) — 8,000 د.ع
• وسط (5–7 أشخاص) — 15,000 د.ع
• كبيرة (8–11 شخص) — 25,000 د.ع

🥐 - الكرواسون المحشي -
🍫 شوكلا — 2,000 د.ع
🧈 لوتس — 2,000 د.ع
🍯 كراميل — 2,000 د.ع

🍩 - الدونات -
🤍 نوتيلا بيضاء — 1,000 د.ع
🍫 نوتيلا — 1,000 د.ع
🍓 فراولة — 1,000 د.ع

🍹 - المشروبات -
🍋 موهيتو
🫐 بلو بيري
🍃 ليمون نعناع
🥤 صودا

💰 سعر المشروبات: 2,500 د.ع

🔥 الكمية محدودة يومياً

✍️ للتثبيت أرسل اسم المنتج المطلوب وسنزودك بالتفاصيل مباشرة."""


        r = requests.post(
            f"https://graph.instagram.com/v23.0/me/messages?access_token={INSTAGRAM_ACCESS_TOKEN}",
            json={
                "recipient": {"id": sender_id},
                "message": {"text": reply}
            }
        )

        print("META STATUS =", r.status_code)
        print("META RESPONSE =", r.text)

    except Exception as e:
        print("ERROR:", e)

    return {"status": "ok"}
