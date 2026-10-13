# db/repository.py
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from db.models import Chunk, Document

async def search_chunks_async(
    session: AsyncSession, 
    query_vector: list[float], 
    top_k: int = 5, 
    min_similarity: float = 0.5
):
    distance = Chunk.embedding.cosine_distance(query_vector)

    cols = [
        Chunk.id,
        Chunk.document_id,
        Chunk.content,
        Chunk.meta,
        (1 - distance).label("similarity"),
    ]

    top = (await session.execute(
        select(*cols).order_by(distance).limit(top_k)
    )).mappings().all()

    top = [r for r in top if r["similarity"] >= min_similarity]
    if not top:
        return []

    sections = list({r["meta"].get("section") for r in top} - {None})
    if not sections:
        return top

    expanded = (await session.execute(
        select(*cols)
        .where(Chunk.meta["section"].as_string().in_(sections))
        .order_by(distance)
    )).mappings().all()

    return expanded

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