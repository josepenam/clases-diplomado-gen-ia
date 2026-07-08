# Módulo 3 · Clase 5 — Deployment

Diplomado de Extensión en IA Generativa para Organizaciones.

This class teaches how to take a GenAI prototype out of a notebook and **put it in production
as an API**: containerize it with Docker, serve a LangChain chain over HTTP, and deploy it to the
cloud (fly.io) with CI. It ends with a 3-week homework that extends the served app into a RAG
system backed by a vector database (Qdrant).

---

## Learning objectives

By the end of the class a student can:

1. Explain why a local model is the *start*, not the end — architecture trade-offs (monolithic vs. distributed), and why deployment matters (latency, uptime, cost, scalability, security).
2. Read and reason about a REST API (endpoint, method, params, status codes).
3. Containerize a Python app with **Docker** (Dockerfile → image → container).
4. Serve a LangChain chain as an HTTP API with **FastAPI**, and try it from the built-in Swagger playground (`/docs`).
5. Deploy that API to **fly.io**, injecting secrets safely, with **GitHub Actions** CI.
6. Consume the deployed API from code (plain HTTP + streaming).
7. Build an agent on a **managed platform** (Claude Managed Agents): sandboxed code execution, web search, and durable server-side **sessions** — and contrast it with self-hosting.
8. (Homework) Build a production RAG pipeline: chunking → embeddings → **Qdrant Cloud** → retrieval.

## Prerequisites

- **Docker** installed (Docker Desktop).
- A **fly.io** account and `flyctl` installed.
- A **GitHub** account (to clone the example projects).
- A local dev environment with **Python > 3.11**.
- API keys: **OpenAI** (required), **Qdrant Cloud** (for the homework), **Anthropic** with Managed Agents beta access (for lección 3).

---

## Repository layout

```
class_3_5_deployment/
├── README.md                          ← this file
├── deck/
│   ├── deck_3_5_deployment.pptx        Main slides (the deployment walkthrough)
│   └── Tarea_RAG.pptx                  Homework brief (RAG)
├── leccion1_docker-hello-world/       LECCIÓN 1 · Docker fundamentals
├── leccion2_serve-chain-api/          LECCIÓN 2 · Serve a chain as an API w/ FastAPI → fly.io
│   └── Test_remote_langchain_client.ipynb   Consume the deployed API (HTTP + streaming)
├── leccion3_anthropic_managed_agents/ LECCIÓN 3 · A hosted agent on Claude Managed Agents
│   └── Test_managed_agent_sessions.ipynb    Consume the managed agent through sessions
├── leccion4_intro_qdrant/             LECCIÓN 4 (tarea) · production RAG over Qdrant Cloud
│   ├── intro_qdrant.ipynb                   load + query a Qdrant Cloud vector store
│   └── trump_speech.txt                     sample corpus for the demo
├── pyproject.toml · uv.lock           Class environment (uv) for the notebooks
└── .env.example                       Template for the secrets the notebooks need (copy → .env)
```

Each lesson below corresponds to a step in the deck.

### Lección 1 — `leccion1_docker-hello-world/`  *(deck: "Paso 1: Docker")*
The smallest possible Docker demo: a Python script that prints a line, plus a `Dockerfile`. Its only
job is to show the build→run loop before applying it to a real app.

```bash
cd leccion1_docker-hello-world
docker build . -t hello-docker
docker run hello-docker        # → "Hello Docker world! This is a test"
```
- Base image is **`python:3.12-slim`**.
- `requirements.txt` is intentionally empty (no dependencies — that's the point).

### Lección 2 — `leccion2_serve-chain-api/`  *(deck: "Paso 2: Servir modelo vía API")*
A FastAPI service that exposes a one-line LangChain (LCEL) summarization chain (`prompt | llm`).
It is deployed to fly.io; the included GitHub Actions workflow redeploys on every push to `main`.
For stateful **agents**, the modern path is **LangGraph** (`langgraph dev`).

Endpoints: `GET /` (health) · `POST /summarize` · `POST /summarize/stream` (SSE) · `GET /docs` (playground).

```bash
cd leccion2_serve-chain-api
cp .env.example .env            # add your OPENAI_API_KEY
poetry install
poetry run uvicorn app.server:app --reload --port 8000
# → open http://localhost:8000/docs  (try POST /summarize)
```
Run in Docker: `docker build . -t serve-chain-api` then
`docker run --env-file .env -p 8080:8080 serve-chain-api` → http://localhost:8080/docs.
Deploy: `fly launch` → `fly secrets set OPENAI_API_KEY=...` (or `flyctl secrets import < .env`) → `fly deploy`.
Consume it from code with `leccion2_serve-chain-api/Test_remote_langchain_client.ipynb` (plain HTTP + streaming — see the *Client demos* below).

### Paso 3 — deploy on fly.io  *(deck: "Paso 3: Deployar API")*
No separate folder, and **no committed `fly.toml`** — the whole point is using the fly CLI:
`fly launch` (run inside `leccion2_serve-chain-api/`) generates each student's own `fly.toml`
with a unique app name, then `fly secrets set OPENAI_API_KEY=...` and `fly deploy`.
- `.github/workflows/fly-deploy.yml` — CI that runs `flyctl deploy` on push to `main` (needs a `FLY_API_TOKEN` repo secret and your generated `fly.toml` committed).

### Lección 3 — `leccion3_anthropic_managed_agents/`  *(deck: "Paso 4: Managed Agents")*
The counterpoint to lección 2: instead of serving the model ourselves, **Anthropic hosts the
whole agent** — brain (agent loop), hands (a cloud sandbox that runs code), and a durable
server-side **session** (append-only event log, the only permanent piece). The demo agent is an
*"Analista Económico Chile"*: its sandbox can only reach the public **mindicador.cl** API
(UF, dólar, UTM, IPC), and `web_search`/`web_fetch` are enabled for broader context.

```bash
cd leccion3_anthropic_managed_agents
cp .env.example .env            # add ANTHROPIC_API_KEY (Managed Agents beta access)
cd .. && uv sync
uv run python leccion3_anthropic_managed_agents/agent.py   # provision once (env + agent)
```
Then the lesson itself runs in `leccion3_anthropic_managed_agents/Test_managed_agent_sessions.ipynb`:
create a session, stream events, download the agent's report, and **resume the same conversation
after a kernel restart** (the state lives in the server-side session, not the client).
Slide content: `leccion3_anthropic_managed_agents/SLIDES.md`.

### Lección 4 (tarea) — `leccion4_intro_qdrant/`  *(deck: "Tarea: Deployar RAG")*
A **Colab-first** notebook that demonstrates the production RAG building blocks: read `trump_speech.txt`
→ chunk with `RecursiveCharacterTextSplitter` → embed with OpenAI `text-embedding-3-large` → upload to a
**Qdrant Cloud** collection → run a similarity search. Credentials come from Colab secrets or a local `.env`.
It's the seed for the 3-week homework (extend it into the served API from lección 2).

- In **Colab**: the first cell auto-installs the required packages — just add `QDRANT_API_KEY`, `QDRANT_URL`, `OPENAI_API_KEY` as secrets and run top to bottom.
- **Locally**: it runs against this folder's uv environment (which has `langchain-qdrant`/`qdrant-client`). Add Jupyter on the fly:
  ```bash
  cp .env.example .env            # add QDRANT_API_KEY, QDRANT_URL, OPENAI_API_KEY
  uv sync
  uv run --with jupyterlab jupyter lab leccion4_intro_qdrant/intro_qdrant.ipynb
  ```

### Client demos — each lives inside its lesson folder

- **`leccion2_serve-chain-api/Test_remote_langchain_client.ipynb`** — consume the deployed API from
  code with plain `requests` (no LangChain needed client-side): **Method 1** a normal `POST /summarize`,
  **Method 2** the streaming `POST /summarize/stream` (SSE). Defaults to the deployed fly.io URL with a
  commented `localhost` option, and notes the fly cold-start (first call wakes the machine).
- **`leccion3_anthropic_managed_agents/Test_managed_agent_sessions.ipynb`** — consume the managed agent
  **through sessions** with the `anthropic` SDK: create a session, stream its events (watching the sandbox
  run code against mindicador.cl), download the report it writes to `/mnt/session/outputs/`, then
  list/replay/resume the session from the server-side event log. Runs on this folder's uv environment.

---

## Environments (important)

This folder is **deliberately isolated** from the repo root because the notebook needs Qdrant packages
and a newer LangChain than the rest of the diploma:

| Scope | Manager / Python | Why |
|---|---|---|
| Repo root `clases/` | Poetry · Python ^3.12 · LangChain 0.3.x | shared base for most classes (has Jupyter, no Qdrant) |
| `class_3_5_deployment/` | **uv** · `>=3.10` · LangChain **1.x** + `qdrant-client` + `anthropic` | runs `leccion4_.../intro_qdrant.ipynb` + `leccion3_.../Test_managed_agent_sessions.ipynb` |
| `leccion2_serve-chain-api/` | **Poetry** · ^3.11 · FastAPI + LangChain **1.x** | the served app (own deploy) |

The notebooks are written for **Google Colab** (the install cell handles setup there), so students don't
have to reconcile these environments to follow along. *Future cleanup (not required for the class): align
the served app and the notebook onto the same pinned LangChain 1.x set and document one canonical env.*

## Secrets

**Never commit a real `.env`.** Each project ships a `.env.example` — copy it to `.env` and fill in your
keys. `.env` is git-ignored at the repo root and inside `leccion2_serve-chain-api/`. In production, inject
secrets via the platform (`fly secrets set ...` / `flyctl secrets import < .env`), never bake them into the image.
