# intro-qdrant  ·  Tarea (RAG en producción)

The homework seed for the class: the building blocks of a **production RAG pipeline** over a
managed vector database (**Qdrant Cloud**). It's the starting point students extend into the
final 3-week assignment (wire this retrieval into the served API from lección 2).

## What it does

`intro_qdrant.ipynb` walks through the load → retrieve loop end to end:

1. **Chunk** — split `trump_speech.txt` with `RecursiveCharacterTextSplitter` (`chunk_size=1000`, `chunk_overlap=200`).
2. **Embed** — OpenAI `text-embedding-3-large`.
3. **Upload** — push the vectors to a **Qdrant Cloud** collection (`QdrantVectorStore.from_documents`).
4. **Query** — `similarity_search` against the existing collection.

## Setup

You need three keys: **`QDRANT_API_KEY`**, **`QDRANT_URL`** (create a free cluster at
[cloud.qdrant.io](https://cloud.qdrant.io)) and **`OPENAI_API_KEY`**.

- **Colab (recommended path in class):** the first cell auto-installs the packages; add the three
  keys as Colab **secrets** and run top to bottom.
- **Local:** runs on the class uv environment (it has `langchain-qdrant` / `qdrant-client`). Put the
  keys in a `.env` here or in the class root (`class_3_5_deployment/.env`), then:
  ```bash
  cd ..                       # class_3_5_deployment/
  cp .env.example .env        # fill in QDRANT_API_KEY, QDRANT_URL, OPENAI_API_KEY
  uv sync
  uv run --with jupyterlab jupyter lab leccion4_intro_qdrant/intro_qdrant.ipynb
  ```
  (Kernel: **Python (clase 3.5)** — see the lección 3 README for registering it.)

## Files

| File | What |
|---|---|
| `intro_qdrant.ipynb` | the notebook (Colab-first, local fallback) |
| `trump_speech.txt` | sample corpus to chunk + embed |
| `.env.example` | template for the three keys |
