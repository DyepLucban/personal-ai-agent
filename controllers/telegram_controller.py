from collections import deque
from fastapi import Request, BackgroundTasks
from agents.main_agent import run_agent
from config.settings import TELEGRAM_API_URL, TELEGRAM_BOT_TOKEN
import httpx

_MAX_SEEN_UPDATES = 1000
_seen_update_ids: set[int] = set()
_seen_update_order: deque[int] = deque()

def _already_processed(update_id: int) -> bool:
    if update_id in _seen_update_ids:
        return True

    _seen_update_ids.add(update_id)
    _seen_update_order.append(update_id)
    if len(_seen_update_order) > _MAX_SEEN_UPDATES:
        oldest = _seen_update_order.popleft()
        _seen_update_ids.discard(oldest)

    return False

async def handle_webhook(request: Request, background_tasks: BackgroundTasks) -> dict:
    try:
        payload = await request.json()
        update_id = payload.get("update_id")
        message = payload.get("message")

        if not message:
            return {"ok": True}

        if update_id is not None and _already_processed(update_id):
            return {"ok": True}

        chat_id = message["chat"]["id"]
        query = message.get("text", "")

        background_tasks.add_task(_process_message, chat_id, query)

        return {"ok": True}
    except OSError as e:
        print(f"Error: {e}")
        return {"status": "error", "code": 500, "message": e}

def _process_message(chat_id, query) -> None:
    try:
        res = run_agent(query)
        bot_reply(chat_id, res["message"])
    except Exception as e:
        print(f"Error processing message: {e}")

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
