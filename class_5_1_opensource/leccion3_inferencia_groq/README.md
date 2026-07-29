# leccion3_inferencia_groq

**Modelos abiertos servidos en la nube a alta velocidad**: consume los `gpt-oss` de OpenAI
(open-weights) a través de la API de [Groq](https://groq.com) con LangChain, y mide la
velocidad real de inferencia en tokens por segundo.

Tercera de las tres lecciones de la Clase 5.1 — el contrapunto de la lección 1: el mismo tipo
de modelo abierto, pero servido por hardware especializado (LPU) a cientos de t/s.

## Qué hace

| Paso | Detalle |
|---|---|
| Setup | Carga `GROQ_API_KEY` (requerida) y `LANGSMITH_API_KEY` (opcional) desde Colab userdata o `.env`. |
| Tracing | Solo se activa si existe `LANGSMITH_API_KEY` (nunca se fuerza). |
| Inferencia | `ChatGroq` con `openai/gpt-oss-20b` y `openai/gpt-oss-120b` sobre la misma traducción ES→EN de la lección 1. |
| Velocidad | t/s reales desde `token_usage.completion_tokens / completion_time` + tabla comparativa. |

## Requisitos

- Python 3.12 y [uv](https://github.com/astral-sh/uv), o Google Colab.
- Cuenta gratuita de Groq y una API key: https://console.groq.com.
- Opcional: cuenta de LangSmith si quieres tracing.

## Configuración

```bash
# 1. Copia la plantilla de secretos y completa tu llave
cp .env.example .env          # edita GROQ_API_KEY (LANGSMITH_API_KEY es opcional)

# 2. Sincroniza el entorno (crea .venv con las dependencias fijadas)
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
```

El `.env` real nunca se versiona (está en `.gitignore`). En Google Colab las llaves se leen
desde `google.colab.userdata` usando los mismos nombres.

## Ejecución local

```bash
# Registra el kernel de Jupyter para este entorno
uv run python -m ipykernel install --user \
  --name clase-5-1-l3 --display-name "Python (clase 5.1 · L3)"

# Abre el notebook
uv run --with jupyterlab jupyter lab inferencia_con_groq.ipynb
```

> Groq rota su catálogo de modelos: si alguno de los `gpt-oss` dejara de estar disponible,
> revisa https://console.groq.com/docs/models y cambia el nombre del modelo en el notebook
> (p. ej. `llama-3.3-70b-versatile` o `llama-3.1-8b-instant`).

## Referencias

- https://console.groq.com/docs/models
- https://docs.langchain.com/oss/python/integrations/chat/groq
- https://console.groq.com/docs/quickstart
