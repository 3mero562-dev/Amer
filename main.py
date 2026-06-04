import json
from fastapi import FastAPI, Request
import requests

BOT_TOKEN =https://api.telegram.org/"bot8876951923:AAFCzlMvrasHtjh68mTau7vjRuBGXp7xBeM"/getUpdates 
CHAT_ID = "5805710703"

app = FastAPI()

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
@app.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return int(challenge)

    return {"error": "Invalid token"}

@app.get("/")
def home():
    return {"status": "working"}


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    print("\n\n========== NEW REQUEST ==========")
    print(json.dumps(data, indent=4, ensure_ascii=False))
    print("=================================\n\n")

    try:
        text = json.dumps(data, indent=4, ensure_ascii=False)

        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": CHAT_ID,
                "text": text[:4000]
            }
        )

    except Exception as e:
        print("Telegram Error:", e)

    return {"status": "ok"}
