from fastapi import FastAPI
from routes import router
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage


app = FastAPI()
app.include_router(router)

@app.get("/")
async def root():
    return {"message": "server is running"}
