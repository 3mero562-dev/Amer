from fastapi import FastAPI, Request

app = FastAPI()

VERIFY_TOKEN = "amer123"


@app.get("/")
def home():
    return {
        "status": "working",
        "message": "AI Bot Ready"
    }


@app.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return int(challenge)

    return {"error": "Invalid token"}


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    print(data)
    return {"status": "ok"}
