from fastapi import Request
from agents.main_agent import run_agent
from config.settings import TELEGRAM_API_URL, TELEGRAM_BOT_TOKEN
import httpx

async def handle_webhook(request: Request) -> dict:
    try:
        payload = await request.json()
        message = payload.get("message")

        if not message:
            return {"ok": True}

        chat_id = message["chat"]["id"]
        query = message.get("text", "")

        # Run the LLM
        res = run_agent(query)

        # Function for the telegram bot to reply
        bot_reply(chat_id, res["message"])

        return {"data": res}
    except OSError as e:
        print(f"Error: {e}")
        return {"status": "error", "code": 500, "message": e}

def bot_reply(chat_id, text) -> dict:
    try:
        httpx.post(f"{TELEGRAM_API_URL}{TELEGRAM_BOT_TOKEN}/sendMessage", json={
            "chat_id": chat_id,
            "text": text
        })

        return {"status":200, "message": "ok"}
    except OSError as e:
        print(f"Error: {e}")
        return {"status": "error", "code": 500, "message": e}

