from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from openai import OpenAI
import os
import json

try:
    import requests
except Exception:
    import httpx

    class _RequestsFallback:
        @staticmethod
        def post(url, json=None, timeout=None):
            return httpx.post(url, json=json, timeout=timeout)

    requests = _RequestsFallback()

OPEN_API_KEY = os.getenv("OPEN_API_KEY")
client = OpenAI(api_key=OPEN_API_KEY)

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
أنت موظف مبيعات لمتجر كوكيز لارين.

إذا كانت الرسالة طلب شراء:
أرجع JSON فقط بهذا الشكل:

{
  "items": [
    {"name":"اسم المنتج","qty":1}
  ]
}

إذا كانت الرسالة سؤال أو استفسار:
أجب بشكل طبيعي ومختصر.

معلومات المتجر:
- سعر التوصيل 2000 د.ع
- مدة التوصيل ساعتين

الأحجام:
فردي
صغير
وسط
كبير

المنتجات:

سخان فردي
سخان صغير
سخان وسط
سخان كبير

كيكة كوكيز فردي
كيكة كوكيز صغير
كيكة كوكيز وسط
كيكة كوكيز كبير

دونات
كرواسون
موهيتو

إذا كتب الزبون:
سخان صغير
أرجع:
{"items":[{"name":"سخان صغير","qty":1}]}

إذا كتب:
كيكة كوكيز وسط
أرجع:
{"items":[{"name":"كيكة كوكيز وسط","qty":1}]}

إذا كتب:
2 موهيتو و3 دونات
أرجع:
{"items":[
{"name":"موهيتو","qty":2},
{"name":"دونات","qty":3}
]}

إذا سأل:
التوصيل مجاني؟

أجب:
لا، سعر التوصيل 2000 د.ع.

إذا سأل:
شكد مدة التوصيل؟

أجب:
مدة التوصيل حوالي ساعتين.
"""
            },
            {
                "role": "user",
                "content": message_text
            }
        ]
    )

    return response.choices[0].message.content

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

    except (KeyError, IndexError):
        return {"status": "ignored"}

    if event.get("message", {}).get("is_echo"):
        return {"status": "echo_ignored"}

    if "message" not in event:
        return {"status": "ignored"}

    message_text = event["message"].get("text", "").strip().lower()
    sender_id = event.get("sender", {}).get("id")

    thanks_words = [
        "شكرا",
        "شكراً",
        "عاشت ايدكم",
        "تسلم",
        "تسلمين",
        "حبيبي",
        "ممنون",
        "مشكور",
        "عاشت ايدك",
        "الله يبارك بيكم",
        "ممتاز",
        "تمام",
        "اوكي",
        "اوك",
        "زين",
        "حلو",
        "ماقصرتوا",
        "ما قصرتوا",
        "كفو",
        "روعة"
    ]

    if any(word in message_text for word in thanks_words):
        return {"status": "ignored"}

    reply = ""

    from datetime import datetime, timedelta

    hour = (datetime.now() + timedelta(hours=3)).hour
    print("CURRENT HOUR =", hour)

   
       
    print("SENDER =", event.get("sender"))
    print("RECIPIENT =", event.get("recipient"))

    if not sender_id or not message_text:
        return {"status": "ignored"}

    print("MESSAGE TEXT =", message_text)
    print("SENDER ID =", sender_id)

    order_data = {"items": []}
    telegram_message = None

    greetings = [
        "مرحبا",
        "هلو",
        "السلام عليكم",
        "سلام",
        "اهلا",
        "أهلا",
        "هاي"
    ]

    product = user_orders.get(sender_id, "منتج غير محدد")

    print("ALL ORDERS =", user_orders)
    print("PRODUCT =", product)

    reply = """🍪 لتثبيت الطلب يرجى إرسال جميع التفاصيل برسالة واحدة:

🍪 المنتجات المطلوبة
📞 رقم الهاتف
📍 العنوان بالتفصيل"""

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

✍️ 🍪 لتثبيت الطلب ارسل التفاصيل والرقم والعنوان برسالة واحدة.
"""
    elif ("07" in message_text or "٠٧" in message_text) and len(message_text) > 15:

        order_data = analyze_order(message_text)

        prices = {
            "سخان فردي": 2500,
            "سخان صغير": 8000,
            "سخان وسط": 15000,
            "سخان كبير": 25000,
            "كوكيز فردي": 2500,
            "كيكة كوكيز صغير": 8000,
            "كيكة كوكيز وسط": 15000,
            "كيكة كوكيز كبير": 25000,
            "كوكيز حجم فردي": 2500,
            "كيكه كوكيز صغير": 8000,
            "كيكه كوكيز وسط": 15000,
            "كيكه كوكيز كبير": 25000,
            "دونات": 1000,
            "كرواسون": 2000,
            "موهيتو": 2500
        }

        delivery_price = 2000
        total_price = 0

        for item in order_data.get("items", []):
            name = item.get("name")
            qty = item.get("qty", 0)

            if name in prices:
                total_price += prices[name] * qty

        grand_total = total_price + delivery_price

        telegram_message = f"""
📦 طلب جديد من الانستغرام

👤 User ID:
{sender_id}

📦 الطلب الكامل:

{message_text}
"""

        reply = f"""✅ تم تثبيت طلبكم بنجاح ❤️🍪

💰 السعر الكلي: {grand_total} د.ع

🚚 سيتم التوصيل خلال ساعتين من تأكيد الحجز"""


