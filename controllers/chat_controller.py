from fastapi import Request
from agents.main_agent import run_agent

async def chat(request: Request) -> dict:
    try:
        data = await request.json()

        res = run_agent(data["query"])

        return {"data": res}
    except OSError as e:
        print(f"Error: {e}")
        return {"status": "error", "code": 500, "message": e}
