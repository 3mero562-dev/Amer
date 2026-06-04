from fastapi import FastAPI, Request
from openai import OpenAI
import json

app = FastAPI()

client = OpenAI(
    api_key="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"
)

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

        message_text = data["entry"][0]["messaging"][0]["message"]["text"]

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

        print("========== AI REPLY ==========")
        print(ai_reply)
        print("==============================")

    except Exception as e:
        print("OPENAI ERROR:", e)

    return {"status": "ok"}
