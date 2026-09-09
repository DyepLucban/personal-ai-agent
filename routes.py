from fastapi import Request, APIRouter
from controllers import chat_controller

router = APIRouter()

@router.get("/health")
async def health():
    return {"status": "ok", "code": 200}

@router.post("/chat")
async def chat(request: Request):
    return await chat_controller.chat(request)