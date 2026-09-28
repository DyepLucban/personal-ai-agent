# tools/database_search_tool.py
from langchain_core.tools import tool

from services.ingestion import embeddings_model
from db.session import SessionSync
from db.repository import search_chunks_sync


@tool
def database_search(query: str) -> str:
    """Search Jeffrey's uploaded documents (e.g. resume/CV) for information
    relevant to the query. Use this whenever the user asks about Jeffrey's
    experience, skills, projects, or background or Jeffrey ask about his resume/cv (
    experience, skills, projects or background)"""
    query_vector = embeddings_model.embed_query(query)

    with SessionSync() as session:
        results = search_chunks_sync(session, query_vector, top_k=5)

    if not results:
        return "No relevant documents found."

    message = "\n\n".join(f"(similarity {sim:.2f}) {chunk.content}" for chunk, sim in results)

    print(f"MESSAGE: {message}")

    return message