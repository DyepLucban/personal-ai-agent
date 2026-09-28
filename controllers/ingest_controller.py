import hashlib

from fastapi import Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_session
from db.repository import (
    get_document_by_hash,
    get_document_by_filename,
    delete_document,
    create_document_with_chunks,
)
from services.ingestion import ingest_data

async def ingest(file: UploadFile, session: AsyncSession = Depends(get_session)):
    raw_bytes = await file.read()
    content_sha256 = hashlib.sha256(raw_bytes).hexdigest()

    existing = await get_document_by_hash(session, content_sha256)
    same_name = None if existing else await get_document_by_filename(session, file.filename)

    await session.rollback()

    if existing:
        return {"status": "unchanged", "document_id": existing.id}

    await file.seek(0)
    chunks = await ingest_data(file)
    raw_text = "\n".join(text for text, _, _ in chunks)

    async with session.begin():
        if same_name:
            await delete_document(session, same_name)
        document = await create_document_with_chunks(
            session,
            filename=file.filename,
            content_sha256=content_sha256,
            raw_text=raw_text,
            chunks=chunks,
        )

    return {"status": "ingested", "document_id": document.id, "chunks": len(chunks)}