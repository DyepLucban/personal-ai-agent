# controllers/search_controller.py
from sqlalchemy.ext.asyncio import AsyncSession

from services.ingestion import embeddings_model
from db.repository import search_chunks_async


async def search(query: str, session: AsyncSession):
    query_vector = embeddings_model.aembed_query(query)

    results = await search_chunks_async(session, query_vector, top_k=5)

    return {
        "query": query,
        "results": [
            {"content": chunk.content, "similarity": round(similarity, 3), "meta": chunk.meta}
            for chunk, similarity in results
        ],
    }