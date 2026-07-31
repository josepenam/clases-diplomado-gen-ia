# leccion6_rag_visual

**RAG visual**: buscar dentro de un PDF por lo que se **ve** — sin OCR. Cada página se
indexa **como imagen** con un embedding multimodal (`gemini-embedding-2`) y se recupera
la página correcta por similitud coseno; la página ganadora se le pasa a **gpt-5** como
imagen para responder con cita de página. Es el patrón **ColPali/ColQwen** (líder del
benchmark ViDoRe) en su versión API, demostrable en vivo sin GPU.

Sexta lección de la Clase 5.3 — la alternativa al parsing de la lección 5: en vez de
convertir el documento a texto, se busca directo sobre los píxeles.

## Qué hace

| Paso | Detalle |
|---|---|
| Setup | Carga `OPENAI_API_KEY` y `GEMINI_API_KEY` desde Colab userdata o `.env`. |
| Documento | `data/documento_ejemplo.pdf` — el mismo PDF chileno con tablas de la lección 5. |
| Rasterizar | `pypdfium2` convierte cada página a PNG (sin OCR, sin parsing). |
| Indexar | Un embedding `gemini-embedding-2` por página-imagen (batches de 6). |
| Consultar | Embedding de la pregunta → similitud coseno con numpy → top-3 páginas. |
| Responder | La página top-1 viaja en base64 a **gpt-5**, que responde citando la página. |
| Mini-eval | 3 preguntas de negocio: una textual, una de tabla y una de gráfico. |

## Requisitos

- Python 3.12 y [uv](https://github.com/astral-sh/uv), o Google Colab.
- API key de OpenAI: https://platform.openai.com.
- API key de Gemini (gratis): https://aistudio.google.com.

## Configuración

```bash
# 1. Copia la plantilla de secretos y completa tus llaves
cp .env.example .env          # edita OPENAI_API_KEY y GEMINI_API_KEY

# 2. Sincroniza el entorno (crea .venv con las dependencias fijadas)
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
```

## Ejecución local

```bash
# Registra el kernel de Jupyter para este entorno
uv run python -m ipykernel install --user \
  --name clase-5-3-l6 --display-name "Python (clase 5.3 · L6)"

# Abre el notebook
uv run --with jupyterlab jupyter lab rag_visual.ipynb
```

## Referencias

- https://ai.google.dev/gemini-api/docs/embeddings
- https://arxiv.org/abs/2407.01449 (ColPali)
- https://huggingface.co/vidore (benchmark ViDoRe)
