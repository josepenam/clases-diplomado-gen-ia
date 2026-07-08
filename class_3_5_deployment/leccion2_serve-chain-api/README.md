# serve-chain-api

A minimal example of **serving a simple LangChain chain as an HTTP API** and deploying it.

It takes the kind of chain you'd normally run inside a notebook and puts it behind a real
web endpoint with **FastAPI**, so any client (a browser, `curl`, another app) can call it.
For stateful **agents**, the modern path is [LangGraph](https://langchain-ai.github.io/langgraph/)
(`langgraph dev`) — but the FastAPI pattern here is the durable, transferable skill.

## What it does

`app/server.py` builds an LCEL chain (`prompt | llm`) and exposes it via FastAPI:

| Route | Method | Purpose |
|---|---|---|
| `/` | GET | Health check |
| `/summarize` | POST | Summarize text sent in the JSON body |
| `/summarize/stream` | POST | Stream the summary token-by-token (SSE) |
| `/docs` | GET | Interactive Swagger UI — the "playground" |

## Setup

Set your environment variable — create a `.env` file (copy `.env.example`):

```
OPENAI_API_KEY=<your-api-key>
```

## Run locally

```bash
poetry install
poetry run uvicorn app.server:app --reload --port 8000
```

Then open the interactive docs at **http://localhost:8000/docs** and try `POST /summarize`,
or from the terminal:

```bash
curl -X POST http://localhost:8000/summarize \
  -H "Content-Type: application/json" \
  -d '{"text": "Long text to summarize here..."}'
```

## Run in Docker

```bash
# Build
docker build . -t serve-chain-api

# Run (inject your key via --env-file)
docker run --env-file .env -p 8080:8080 serve-chain-api
```

Then open **http://localhost:8080/docs**.

## Deploy on fly.io

There is deliberately **no `fly.toml` in this repo** — `fly launch` generates yours:

```bash
fly launch            # pick a UNIQUE app name (e.g. serve-chain-api-<tu-nombre>); creates fly.toml
fly secrets set OPENAI_API_KEY=<your-api-key>   # or: flyctl secrets import < .env
fly deploy
```

App names are global on fly.io, so everyone in the class needs their own. The generated
`fly.toml` is your app's config (region, `internal_port = 8080` to match the Dockerfile,
auto start/stop) — commit it if you want CI deploys.

The included `.github/workflows/fly-deploy.yml` redeploys automatically on push to `main`
(requires a `FLY_API_TOKEN` repo secret **and** your committed `fly.toml`).

## Consume it from a notebook

`Test_remote_langchain_client.ipynb` (in this folder) calls the deployed API from code with plain
`requests` — no LangChain needed client-side: **Método 1** a normal `POST /summarize`, **Método 2**
the streaming `POST /summarize/stream` (SSE). It defaults to the deployed fly.io URL (with a commented
`localhost:8000` option) and notes the fly cold-start on the first call.
