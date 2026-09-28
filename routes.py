from fastapi import Request, APIRouter, File, UploadFile, Depends, BackgroundTasks
from controllers import chat_controller, telegram_controller, ingest_controller
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_session

router = APIRouter()

@router.get("/health")
async def health():
    return {"status": "ok", "code": 200}

@router.post("/chat")
async def chat(request: Request):
    return await chat_controller.chat(request)

@router.post("/webhook/telegram")
async def handle_webhook(request: Request, background_tasks: BackgroundTasks):
    return await telegram_controller.handle_webhook(request, background_tasks)

@router.post("/upload_file")
async def upload_cv(file: UploadFile = File(...), session: AsyncSession = Depends(get_session)):
    return await ingest_controller.ingest(file, session)