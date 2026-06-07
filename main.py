from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from openai import OpenAI
import os, json, requests

app = FastAPI()

VERIFY_TOKEN = "amer123"
OPEN_API_KEY = os.getenv("OPEN_API_KEY")
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

client = OpenAI(api_key=OPEN_API_KEY)

def ask_ai(message_text):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": """
أنت موظف مبيعات لمتجر كوكيز لارين.

إذا كانت الرسالة طلب وفيها رقم هاتف وعنوان:
أرجع JSON فقط بهذا الشكل:
{"items":[{"name":"اسم المنتج","qty":1}]}

إذا كانت الرسالة سؤال أو استفسار أو ترحيب:
أجب كنفس موظف المتجر.

سعر التوصيل 2000 دينار.
مدة التوصيل ساعتين.
"""
            },
            {"role": "user", "content": message_text}
        ]
    )

    content = response.choices[0].message.content

    try:
        return json.loads(content)
    except:
        return {"reply": content}

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

@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()

    try:
        event = data["entry"][0]["messaging"][0]
    except:
        return {"status": "ignored"}

    if event.get("message", {}).get("is_echo"):
        return {"status": "echo"}

    sender_id = event.get("sender", {}).get("id")
    message_text = event.get("message", {}).get("text", "")

    if not sender_id or not message_text:
        return {"status": "ignored"}

    result = ask_ai(message_text)

    telegram_message = None

    if "items" in result:

        prices = {
            "سخان فردي": 2500,
            "سخان صغير": 8000,
            "سخان وسط": 15000,
            "سخان كبير": 25000,
            "كيكة كوكيز فردي": 2500,
            "كيكة كوكيز صغير": 8000,
            "كيكة كوكيز وسط": 15000,
            "كيكة كوكيز كبير": 25000,
            "دونات": 1000,
            "كرواسون": 2000,
            "موهيتو": 2500
        }

        total = 2000

        for item in result["items"]:
            name = item.get("name")
            qty = item.get("qty", 1)

            if name in prices:
                total += prices[name] * qty

        reply = f"✅ تم تثبيت طلبكم بنجاح\\n💰 السعر الكلي: {total} د.ع"

        telegram_message = f"""
طلب جديد

User:
{sender_id}

{message_text}
"""

    else:
        reply = result.get("reply", "أهلاً وسهلاً بكم")

    if telegram_message and TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": telegram_message
            }
        )

    requests.post(
        f"https://graph.instagram.com/v23.0/me/messages?access_token={INSTAGRAM_ACCESS_TOKEN}",
        json={
            "recipient": {"id": sender_id},
            "message": {"text": reply}
        }
    )

    return {"status": "ok"}
