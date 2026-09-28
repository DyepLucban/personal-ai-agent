# db/repository.py
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from db.models import Chunk, Document


def _search_stmt(query_vector: list[float], top_k: int) -> Select:
    distance = Chunk.embedding.cosine_distance(query_vector)
    return select(Chunk, (1 - distance).label("similarity")).order_by(distance).limit(top_k)


async def search_chunks_async(session: AsyncSession, query_vector: list[float], top_k: int = 5):
    result = await session.execute(_search_stmt(query_vector, top_k))
    return result.all()


def search_chunks_sync(session: Session, query_vector: list[float], top_k: int = 5):
    result = session.execute(_search_stmt(query_vector, top_k))
    return result.all()


async def get_document_by_hash(session: AsyncSession, content_sha256: str) -> Document | None:
    result = await session.execute(select(Document).where(Document.content_sha256 == content_sha256))
    return result.scalar_one_or_none()


async def get_document_by_filename(session: AsyncSession, filename: str) -> Document | None:
    result = await session.execute(select(Document).where(Document.filename == filename))
    return result.scalar_one_or_none()


async def delete_document(session: AsyncSession, document: Document) -> None:
    await session.delete(document)


async def create_document_with_chunks(
    session: AsyncSession,
    filename: str,
    content_sha256: str,
    raw_text: str,
    chunks: list[tuple[str, list[float], dict]],  # (text, embedding, meta) per chunk
) -> Document:
    document = Document(filename=filename, content_sha256=content_sha256, raw_text=raw_text)
    document.chunks = [Chunk(content=t, embedding=e, meta=m) for t, e, m in chunks]
    session.add(document)
    await session.flush()
    return document