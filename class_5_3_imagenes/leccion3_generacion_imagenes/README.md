# leccion3_generacion_imagenes

**Generación de imágenes desde texto**: GPT-5 orquesta la herramienta `image_generation`
(modelo **gpt-image-1**) a través de la Responses API de OpenAI, todo desde LangChain. El
notebook genera una imagen, la muestra y la guarda en `../outputs/`.

Tercera de las cuatro lecciones de la Clase 5.3 — la contracara de la lección 2: en vez de
entender imágenes, producirlas. En el deck es el arco VAEs → GANs → difusión; aquí se usa el
resultado comercial de esa historia.

## Qué hace

| Paso | Detalle |
|---|---|
| Setup | Carga `OPENAI_API_KEY` desde Colab userdata o `.env`. |
| Tool | `image_generation` (gpt-image-1, 1024×1024, calidad alta) atado a GPT-5 con `bind_tools`. |
| Generación | El LLM interpreta el pedido y llama al generador; la imagen vuelve en base64. |
| Salida | Se muestra inline y se guarda en `../outputs/perros_poker.jpg`. |

> **IMPORTANTE:** para usar `gpt-image-1` OpenAI exige una **organización verificada**
> (validación de identidad en la consola), y cada imagen cuesta dinero (~US$0.17 en calidad
> alta 1024×1024). Para iterar barato, baja `quality` a `"medium"` o `"low"`.

## Requisitos

- Python 3.12 y [uv](https://github.com/astral-sh/uv), o Google Colab.
- API key de OpenAI con organización verificada: https://platform.openai.com.

## Configuración

```bash
# 1. Copia la plantilla de secretos y completa tu llave
cp .env.example .env          # edita OPENAI_API_KEY

# 2. Sincroniza el entorno (crea .venv con las dependencias fijadas)
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
```

## Ejecución local

```bash
# Registra el kernel de Jupyter para este entorno
uv run python -m ipykernel install --user \
  --name clase-5-3-l3 --display-name "Python (clase 5.3 · L3)"

# Abre el notebook
uv run --with jupyterlab jupyter lab generacion_de_imagenes.ipynb
```

## Referencias

- https://platform.openai.com/docs/guides/image-generation
- https://docs.langchain.com/oss/python/integrations/chat/openai
