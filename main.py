from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import requests
import json

app = FastAPI()

VERIFY_TOKEN = "amer123"

BOT_TOKEN = "8876951923:AAFCzlMvrasHtjh68mTau7vjRuBGXp7xBeM"
CHAT_ID = "5805710703"

ACCESS_TOKEN = "IGAAjO1g9T9WRBZAGE0TDFoUDFnWFZAlY3RVOFV6bi01ZAWY1ZAlNJQ1RmSEswdFRmWFNabkI3SjVnNVE5dDRycUlrWXpvREhCNjFaSWlCNG5wclY1N19VVHkyUzBSQ1FGTl9NS3lkczRMY3ZANNGxQWkJBZAmlDRnJrMklXeFlJb2FHRQZDZD"


@app.get("/")
async def home():
    return {"status": "working"}


@app.get("/webhook")
async def verify_webhook(request: Request):

    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(content=challenge)

    return {"error": "verification failed"}


@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()

    print("\n========== INSTAGRAM EVENT ==========")
    print(json.dumps(data, indent=4, ensure_ascii=False))
    print("=====================================\n")

    try:
    sender_id = data["entry"][0]["messaging"][0]["sender"]["id"]

    response = requests.post(
        "https://graph.facebook.com/v23.0/me/messages",
        params={
            "access_token": ACCESS_TOKEN
        },
        json={
            "recipient": {
                "id": sender_id
            },
            "message": {
                "text": "أهلاً بك في كوكيز لارين 🍪"
            }
        },
        timeout=10
    )

    print("STATUS:", response.status_code)
    print("RESPONSE:", response.text)

except Exception as e:
    print("INSTAGRAM REPLY ERROR:", e)

    return {"status": "ok"}
