# Personal AI Agent

Personal AI Agent created from python, FastAPI, Langchain and Docker Model Runner

## Docker Runner Model
Download docker desktop, then go to Models > Docker Hub and install the LLM that fits your machine.

set the downloaded model to `RUNNER_MODEL` with the `RUNNER_MODEL_BASE_URL` of `http://host.docker.internal:12434/v1`

## Current implemented tools
- Weather API
- Random Joke API
- Github (create issue just for now)

## Run the app
Run `docker compose up --build`

then make a request, `http:localhost:8000/chat` with json body of:

```
{
    "query": "You query here"
}
```