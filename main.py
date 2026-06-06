from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from openai import OpenAI
import requests
import os
import json
OPEN_API_KEY = os.getevn("OPEN_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)


app = FastAPI()

user_orders = {}

VERIFY_TOKEN = "amer123"
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def analyze_order(message_text):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": """
استخرج الطلب من رسالة الزبون وأرجع JSON فقط.

مثال:
{
  "items": [
    {"name":"سخان وسط","qty":1},
    {"name":"دونات","qty":2},
    {"name":"موهيتو","qty":2}
  ]
}
"""
            },
            {
                "role": "user",
                "content": message_text
            }
        ]
    )

    return json.loads(response.choices[0].message.content)

@app.get("/")
def home():
    return {"status": "working"}


@app.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(challenge or "")

    return {"error": "Invalid token"}

seen_users = set()
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    print("NEW REQUEST")
    print(data)

    try:
        event = data.get("entry", [{}])[0].get("messaging", [{}])[0]

        if "message" not in event:
            return {"status": "ignored"}

        message_text = event["message"].get("text", "").strip().lower()
        sender_id = event.get("sender", {}).get("id")

        if not sender_id or not message_text:
            return {"status": "ignored"}

        print("MESSAGE TEXT =", message_text)
        print("SENDER ID =", sender_id)

        greetings = ["مرحبا", "هلو", "السلام عليكم", "سلام", "اهلا", "أهلا", "هاي"]

        if sender_id not in seen_users or any(word in message_text for word in greetings):
            seen_users.add(sender_id)

            reply = """
🍪❤️ هلا وغلا

🤤🔥 نورتوا كوكيز لارين

🍪 - سخان كيكة كوكيز -

• فردي (شخص) — 2,500 د.ع
• صغيرة (3-4 أشخاص) — 8,000 د.ع
• وسط (5-7 أشخاص) — 15,000 د.ع
• كبيرة (8-11 شخص) — 25,000 د.ع

🥐 - الكرواسون المحشي -

🍫 شوكلا — 2,000 د.ع
🧀 لوتس — 2,000 د.ع
🍯 كراميل — 2,000 د.ع

🍩 - الدونات -

🤍 نوتيلا بيضاء — 1,000 د.ع
🍫 نوتيلا — 1,000 د.ع
🍓 فراولة — 1,000 د.ع

🍹 - المشروبات -

🍋 موهيتو
🥤 بلو بيري
🍃 ليمون نعناع
🥤 صودا

💰 سعر المشروبات: 2,500 د.ع

🔥 الكمية محدودة يومياً

✍️ للتثبيت أرسل اسم المنتج المطلوب وسنزودك بالتفاصيل مباشرة.
"""

        elif "سخان وسط" in message_text:
            user_orders[sender_id] = "سخان وسط"
            reply = """👥 يكفي 5–7 أشخاص

💰 السعر: 15000 د.ع

📞📍 للتثبيت يرجى إرسال رقم الهاتف والعنوان."""

        elif "سخان صغير" in message_text:
            user_orders[sender_id] = "سخان صغير"
            reply = """👥 يكفي 3–4 أشخاص

💰 السعر: 8000 د.ع

📞📍 للتثبيت يرجى إرسال رقم الهاتف والعنوان."""

        elif "سخان كبير" in message_text:
            user_orders[sender_id] = "سخان كبير"
            reply = """👥 يكفي 8–11 شخص

💰 السعر: 25000 د.ع

📞📍 للتثبيت يرجى إرسال رقم الهاتف والعنوان."""

        elif "فردي" in message_text:
            user_orders[sender_id] = "فردي"
            reply = """👤 يكفي شخص واحد

💰 السعر: 2500 د.ع

📞📍 للتثبيت يرجى إرسال رقم الهاتف والعنوان."""

        elif any(word in message_text for word in ["التوصيل", "سعر التوصيل", "شكد التوصيل", "اجور التوصيل"]):
            reply = """🚚 عرض التوصيل حالياً 2000 دينار فقط ❤️

يشمل جميع مناطق كربلاء 🌹"""

        elif sender_id in user_orders and len(message_text) > 10 and any(char.isdigit() for char in message_text):
            product = user_orders.get(sender_id, "منتج غير محدد")

            reply = """✅ تم تثبيت طلبكم بنجاح ❤️🍪

🚚 سيتم التوصيل خلال ساعتين من تأكيد الحجز"""

            telegram_message = f"""
📦 طلب جديد من الانستغرام

🍪 المنتج:
{product}

👤 User ID:
{sender_id}

📱 الرقم والعنوان:
{message_text}
"""

            if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
                tg_response = requests.post(
                    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": TELEGRAM_CHAT_ID,
                        "text": telegram_message
                    },
                    timeout=10
                )

                print("TELEGRAM STATUS =", tg_response.status_code)
                print("TELEGRAM RESPONSE =", tg_response.text)
            else:
                print("TELEGRAM ERROR: Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")

            user_orders.pop(sender_id, None)

        else:
            reply = "🍪 ارسل اسم المنتج فقط للتثبيت"

        if not INSTAGRAM_ACCESS_TOKEN:
            print("INSTAGRAM ERROR: Missing INSTAGRAM_ACCESS_TOKEN")
            return {"status": "error", "message": "Missing Instagram access token"}

        meta_response = requests.post(
            f"https://graph.instagram.com/v23.0/me/messages?access_token={INSTAGRAM_ACCESS_TOKEN}",
            json={
                "recipient": {"id": sender_id},
                "message": {"text": reply}
            },
            timeout=10
        )

        print("META STATUS =", meta_response.status_code)
        print("META RESPONSE =", meta_response.text)

    except Exception as e:
        print("ERROR:", e)

    return {"status": "ok"}
