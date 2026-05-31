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
def verify_webhook(hub_mode: str = None,
                   hub_verify_token: str = None,
                   hub_challenge: str = None):

    if hub_verify_token == VERIFY_TOKEN:
        return int(hub_challenge)

    return {"error": "Invalid token"}

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    print(data)
    return {"status": "ok"}
