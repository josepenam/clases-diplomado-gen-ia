# leccion5_parsing_agentico

**Caso práctico — parsing agéntico de documentos**: la lección 4 extrajo un formulario de
**1 página**; el negocio real son **PDFs largos con tablas**. Aquí pasamos un mismo
documento público chileno (un capítulo del **IPoM de junio 2026** del Banco Central) por
tres niveles de extracción y comparamos calidad, costo y esfuerzo.

Quinta lección de la Clase 5.2 — la continuación natural del OCR semántico: de una imagen
suelta a un pipeline de documentos.

## Qué hace

| Nivel | Herramienta | Resultado |
|---|---|---|
| Setup | Carga `OPENAI_API_KEY` y `LLAMA_CLOUD_API_KEY` desde Colab userdata o `.env`. | |
| 0 | `pypdf` — texto embebido | Gratis e instantáneo. Los números **sí** aparecen (el PDF es nativo digital), pero el encabezado multinivel se aplasta, nada declara "esto es una tabla" y los gráficos quedan como sopa de cifras. |
| 1 | DIY visual: `pypdfium2` rasteriza la página → `gpt-5-mini` la transcribe a Markdown | La tabla vuelve **con estructura**; fiel para **una** página, pero no escala solo. |
| 2 | **LlamaParse v2** — tier `fast` vs tier `agentic`, lado a lado | El pipeline industrial: capa de texto + screenshot por página, bucle que verifica y reintenta. |
| Cierre | Mercado (LlamaParse, Mistral OCR 4, Azure Document Intelligence, Google Document AI, LiteParse) y el criterio **volumen × complejidad × auditabilidad**. | |

> Nota pedagógica deliberada: el nivel 0 **no** fracasa de forma espectacular con este
> documento, y eso es parte de la lección — no todo PDF necesita IA. Lo que sí se rompe es
> la *estructura* (qué cifra corresponde a qué año) y los gráficos; con un PDF escaneado el
> nivel 0 devolvería vacío.

El documento de ejemplo (`data/documento_ejemplo.pdf`) es el capítulo II del IPoM de junio
2026 del Banco Central de Chile: **9 páginas con 4 tablas y 7 gráficos**, recortado con
`pypdf`. La fuente exacta está documentada en el notebook. La página de trabajo es la **2**
(texto corrido + TABLA II.1 con encabezados de dos niveles + GRÁFICO II.1).

## Requisitos

- Python 3.12 y [uv](https://github.com/astral-sh/uv), o Google Colab.
- API key de OpenAI: https://platform.openai.com (niveles 0 y 1).
- API key de LlamaCloud: https://cloud.llamaindex.ai — plan **Free**, 10.000 créditos/mes
  sin tarjeta (nivel 2). Sin ella, el notebook corre igual: las celdas de LlamaParse se
  saltan con una instrucción clara.

## Configuración

```bash
# 1. Copia la plantilla de secretos y completa tus llaves
cp .env.example .env          # edita OPENAI_API_KEY y LLAMA_CLOUD_API_KEY

# 2. Sincroniza el entorno (crea .venv con las dependencias fijadas)
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
```

## Ejecución local

```bash
# Registra el kernel de Jupyter para este entorno
uv run python -m ipykernel install --user \
  --name clase-5-2-l5 --display-name "Python (clase 5.2 · L5)"

# Abre el notebook
uv run --with jupyterlab jupyter lab parsing_agentico.ipynb
```

## Referencias

- https://developers.llamaindex.ai/llamaparse/
- https://www.bcentral.cl/contenido/-/detalle/publicaciones/politica-monetaria/ipom-junio-2026
- https://mistral.ai/news/mistral-ocr
- https://learn.microsoft.com/azure/ai-services/document-intelligence/
