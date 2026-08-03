# leccion2_vision_llm

**Entendimiento de imágenes con un LLM multimodal**: pásale una imagen a **GPT-5** — por URL
o codificada en base64 — dentro de un `HumanMessage` de LangChain, y conversa sobre lo que
"ve".

Segunda de las seis lecciones de la Clase 5.2 — el salto del detector de clases fijas
(lección 1) a un modelo que describe, razona y responde preguntas abiertas sobre la imagen.

## Qué hace

| Paso | Detalle |
|---|---|
| Setup | Carga `OPENAI_API_KEY` desde Colab userdata o `.env`. |
| Imagen | `Cachureos2020.jpg` local (si falta, se descarga desde Wikimedia). |
| Base64 | La imagen entra como bloque `{type: image, source_type: base64}` junto al texto. |
| URL | La misma imagen referenciada por URL — sin codificar nada. |

## Requisitos

- Python 3.12 y [uv](https://github.com/astral-sh/uv), o Google Colab.
- API key de OpenAI: https://platform.openai.com.

## Configuración

```bash
# 1. Copia la plantilla de secretos y completa tu llave
cp .env.example .env          # edita OPENAI_API_KEY

# 2. Sincroniza el entorno (crea .venv con las dependencias fijadas)
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
```

El `.env` real nunca se versiona (está en `.gitignore`). En Google Colab la llave se lee
desde `google.colab.userdata` con el mismo nombre.

## Ejecución local

```bash
# Registra el kernel de Jupyter para este entorno
uv run python -m ipykernel install --user \
  --name clase-5-2-l2 --display-name "Python (clase 5.2 · L2)"

# Abre el notebook
uv run --with jupyterlab jupyter lab entendimiento_de_imagenes.ipynb
```

## Referencias

- https://docs.langchain.com/oss/python/integrations/chat/openai
- https://platform.openai.com/docs/guides/images-vision
