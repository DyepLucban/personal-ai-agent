from services.doc_ingestion import get_content
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import TokenTextSplitter
from config.settings import RUNNER_EMBEDDING_MODEL, RUNNER_MODEL_BASE_URL
import asyncio

embeddings_model = OpenAIEmbeddings(
    model=RUNNER_EMBEDDING_MODEL, 
    base_url=RUNNER_MODEL_BASE_URL,
    api_key="not-needed",  
    check_embedding_ctx_length=False
)
splitter = TokenTextSplitter(chunk_size=300, chunk_overlap=30)

async def ingest_data(file):
    content = await get_content(file)

    texts, metadatas = [], []
    for data in content["chunks"]:
        text = data["text"]
        for sub_text in splitter.split_text(text):
            texts.append(sub_text)
            metadatas.append(data["metadata"])

    vectors = await embeddings_model.aembed_documents(
        [f"search_document: {t}" for t in texts]
    )

    return list(zip(texts, vectors, metadatas))