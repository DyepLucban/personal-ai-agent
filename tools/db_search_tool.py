# tools/database_search_tool.py
from langchain_core.tools import tool

from services.ingestion import embeddings_model
from db.session import AsyncSessionLocal
from db.repository import search_chunks_async


@tool
async def database_search(query: str) -> str:
    """Search Jeffrey's uploaded documents (e.g. resume/CV) for information
    relevant to the query. Use this whenever the user asks about Jeffrey's
    experience, skills, projects, or background or Jeffrey ask about his resume/cv (
    experience, skills, projects or background)"""
    query_vector = await embeddings_model.aembed_query(query)

    async with AsyncSessionLocal() as session:
        results = await search_chunks_async(session, query_vector, top_k=5)

    if not results:
        return "No relevant documents found."

    message = "\n\n".join(
        f"(similarity {r['similarity']:.2f}) {r['content']}" for r in results
    )

    print(f"MESSAGE: {message}")

    return message