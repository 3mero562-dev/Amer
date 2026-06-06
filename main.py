from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from openai import OpenAI
import os
import json
try:
    import requests
except Exception:
    # Fallback to httpx if requests is not available or cannot be resolved
    import httpx

    class _RequestsFallback:
        @staticmethod
        def post(url, json=None, timeout=None):
            # httpx.post returns a Response object similar enough for our usage
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
        if event.get("message", {}).get("is_echo"):
            return {"status": "echo_ignored"}
        if "message" not in event:
            return {"status": "ignored"}

        message_text = event["message"].get("text", "").strip().lower()
        sender_id = event.get("sender", {}).get("id")
        from datetime import datetime

        hour = datetime.now().hour
        
        if hour < 14 or hour >= 22:
            reply = """
        نعتذر منكم 🙏
        
        حالياً التوصيل متوقف، ويبدأ يومياً من الساعة 3:00 عصراً إلى 10:00 مساءً 🌙
        
        ✨ للحجز المسبق يرجى إرسال المعلومات التالية:
        
        📏 الحجم أو الطلب:
        📞 رقم الهاتف:
        📍 العنوان بالتفصيل:
        ⏰ الوقت المطلوب للاستلام أو التوصيل:
        
        شكراً لاختياركم كوكيز لارين ❤️🍪
        """
        print("SENDER =", event.get("sender"))
        print("RECIPIENT =", event.get("recipient"))
        if not sender_id or not message_text:
            return {"status": "ignored"}

        print("MESSAGE TEXT =", message_text)
        print("SENDER ID =", sender_id)
        order_data = {"items": []}
        telegram_message = None
        greetings = ["مرحبا", "هلو", "السلام عليكم", "سلام", "اهلا", "أهلا", "هاي"]
        product = user_orders.get(sender_id, "منتج غير محدد")
        print("ALL ORDERS =", user_orders)
        print("PRODUCT =", product)
        reply = "🍪 لتثبيت الطلب ارسل التفاصيل والرقم والعنوان برساله واحدة"

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
        elif any(word in message_text for word in [
            "سخان صغير",
            "سخان وسط",
            "سخان كبير",
            "فردي",
            "صغيرة",
            "وسط",
            "موهيتو",
        "بلو بيري",
        "ليمون نعناع",
        "صودا",
        "نوتيلا",
        "نوتيلا بيضاء",
        "فراولة",
            "كبيرة"
]):
            user_orders[sender_id] = message_text
            product = message_text

            reply = """
نعتذر منكم 🙏 حالياً التوصيل متوقف
ويبلش يومياً من الساعة 3 الظهر إلى 10 ليلاً 🌙

✨ للحجز المسبق:
يرجى إرسال المعلومات التالية حتى نثبت الطلب:

📏 الحجم:
📞 رقم الهاتف:
📍 العنوان بالتفصيل:
⏰ الوقت المطلوب للاستلام/التوصيل:
"""
        elif any(word in message_text for word in [ "سعر التوصيل", "شكد التوصيل", "اجور التوصيل"]):
            reply = """🚚 عرض التوصيل حالياً 2000 دينار فقط ❤️

يشمل جميع مناطق كربلاء 🌹"""

        elif any(word in message_text for word in ["متى يوصل", "شكد وقت التوصيل", "وقت التوصيل", "التوصيل شكد", "بعد شكد ","شكد ويوصلني", "شكد يوصل", "شكد ويوصلني الطلب"]):
            reply = "🚚 مدة التوصيل من ساعة إلى ساعتين بعد تأكيد الحجز ❤️🍪"
        elif len(message_text) > 15:
            order_data = analyze_order(message_text)
            telegram_message = f"""
            📦 طلب جديد من الانستغرام
            
            👤 User ID:
            {sender_id}
            
            📦 الطلب الكامل:

            {message_text}
            
        
            """
                        
            reply = """✅ تم تثبيت طلبكم بنجاح ❤️🍪
                    
                    🚚 سيتم التوصيل خلال ساعتين من تأكيد الحجز"""
                    

        if telegram_message and TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
            tg_response = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": telegram_message
        },
        timeout=10
    )

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
