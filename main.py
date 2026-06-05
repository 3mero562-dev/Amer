from fastapi import FastAPI, Request
from openai import OpenAI
import json
import os
import requests

INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
print("TOKEN RAW =", repr(INSTAGRAM_ACCESS_TOKEN))
print("TOKEN EXISTS:", INSTAGRAM_ACCESS_TOKEN is not None)
print("TOKEN START:", INSTAGRAM_ACCESS_TOKEN[:20] if INSTAGRAM_ACCESS_TOKEN else "NONE")
print("TOKEN LENGTH:", len(INSTAGRAM_ACCESS_TOKEN) if INSTAGRAM_ACCESS_TOKEN else 0)
app = FastAPI()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

print("OPENAI CLIENT LOADED")

VERIFY_TOKEN = "amer123"

STORE_INFO = """
أهلاً بك في كوكيز لارين 🍪

⏰ أوقات العمل: من 3 عصراً إلى 10 مساءً

- سخان كيكة كوكيز -
• شخص واحد — 2500 د.ع
• صغيرة (3-4 أشخاص) — 8000 د.ع
• وسط (5-7 أشخاص) — 15000 د.ع
• كبيرة (8-11 شخص) — 25000 د.ع

- الكرواسون المحشي -
شوكلا — 2000 د.ع
لوتس — 2000 د.ع
كراميل — 2000 د.ع

- الدونات -
نوتيلا بيضاء — 1000 د.ع
نوتيلا — 1000 د.ع
فراولة — 1000 د.ع

- المشروبات -
موهيتو
بلو بيري
ليمون نعناع
صودا

السعر 2500 د.ع

🔥 الكمية محدودة يومياً
"""

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

    print("\n========== NEW REQUEST ==========")
    print(json.dumps(data, indent=4, ensure_ascii=False))
    print("=================================\n")

    try:
        event = data["entry"][0]["messaging"][0]

    if "message" not in event:
    return {"status": "ignored"}

message_text = event["message"].get("text", "")

        response = client.responses.create(
            model="gpt-5-mini",
            input=f"""
أنت موظف خدمة زبائن لمحل كوكيز لارين.

معلومات المحل:
{STORE_INFO}

رسالة الزبون:
{message_text}

جاوب باللهجة العراقية وباختصار.
"""
        )

        ai_reply = response.output_text
        print(ai_reply)

        sender_id = data["entry"][0]["messaging"][0]["sender"]["id"]

        r = requests.post(
            f"https://graph.facebook.com/v23.0/me/messages?access_token={INSTAGRAM_ACCESS_TOKEN}",
            json={
                "recipient": {"id": sender_id},
                "message": {"text": ai_reply}
            }
        )

        print("META STATUS:", r.status_code)
        print("META RESPONSE:", r.text)

    except Exception as e:
        print("OPENAI ERROR TYPE:", type(e))
        print("OPENAI ERROR:", repr(e))

    return {"status": "ok"}

import uvicorn

if __name__ == "__main__":
    print("STARTING SERVER...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
