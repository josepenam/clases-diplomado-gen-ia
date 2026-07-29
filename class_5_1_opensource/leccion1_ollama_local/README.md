# leccion1_ollama_local

**Corre un LLM open source en tu máquina con Ollama y consúmelo desde LangChain** — sin API
keys, sin costo por token y sin que tus datos salgan de tu computador.

Primera de las tres lecciones de la Clase 5.1. Aquí el modelo vive **en tu hardware**; en la
lección 3 verás los mismos modelos abiertos servidos en la nube (Groq) a cientos de tokens
por segundo.

## Qué es Ollama

[Ollama](https://ollama.com) es un runtime open source para ejecutar LLMs open-weights (Llama,
Gemma, Qwen, gpt-oss, …) localmente. Instala un servidor local que expone una API HTTP en
`http://localhost:11434`, gestiona la descarga de modelos desde su
[catálogo](https://ollama.com/library) y los ejecuta aprovechando tu GPU (Metal en Apple
Silicon, CUDA en NVIDIA) o tu CPU. Todo corre offline: privacidad total y costo cero por token.

## Instalación

- **macOS:** descarga la app desde https://ollama.com/download (o `brew install ollama`).
- **Windows:** instalador en https://ollama.com/download/windows.
- **Linux:** `curl -fsSL https://ollama.com/install.sh | sh`.

Verifica la instalación:

```bash
ollama --version
```

## Cargar y correr un modelo en tu máquina

```bash
# Descarga el modelo de la lección (~2.0 GB, una sola vez)
ollama pull llama3.2

# Chat interactivo en la terminal (sal con /bye)
ollama run llama3.2

# Ver los modelos descargados
ollama list
```

Con la app abierta (o `ollama serve` en una terminal) el servidor queda escuchando en
`http://localhost:11434` — eso es lo que consume el notebook.

## Qué hace

| Paso | Detalle |
|---|---|
| Chequeo | Verifica que el servidor local responda y que el modelo esté descargado. |
| Invocación | `ChatOllama(model="llama3.2")` con la misma interfaz LangChain que OpenAI/Anthropic. |
| Streaming | `.stream()` — la respuesta token a token. |
| Velocidad | Calcula los t/s locales desde `eval_count` / `eval_duration`, para comparar con Groq (lección 3). |

## Requisitos

- Python 3.12 y [uv](https://github.com/astral-sh/uv).
- Ollama instalado y corriendo, con `llama3.2` descargado (~2.0 GB).
- **Sin API keys** — esta lección no usa `.env`.

## Configuración

```bash
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
```

## Ejecución local

```bash
# Registra el kernel de Jupyter para este entorno
uv run python -m ipykernel install --user \
  --name clase-5-1-l1 --display-name "Python (clase 5.1 · L1)"

# Abre el notebook
uv run --with jupyterlab jupyter lab inferencia_local_con_ollama.ipynb
```

> Esta lección es **local-first** (correr el modelo en TU máquina es el punto): a diferencia
> del resto del repo, no está pensada para Colab. Cambia la variable `MODEL` del notebook por
> cualquier modelo de `ollama list`.

## Referencias

- https://ollama.com/library/llama3.2
- https://docs.ollama.com/api
- https://docs.langchain.com/oss/python/integrations/chat/ollama
