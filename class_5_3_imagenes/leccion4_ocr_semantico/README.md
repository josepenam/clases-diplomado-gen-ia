# leccion4_ocr_semantico

**Caso práctico — OCR semántico**: extraer datos **estructurados** (JSON con esquema
Pydantic) desde un formulario de inspección vehicular escaneado, con letra manuscrita y
opciones marcadas a mano, usando **gpt-5-mini** + `with_structured_output()`.

Cuarta lección de la Clase 5.3 — el caso de negocio que junta todo: la visión multimodal de
la lección 2 aplicada a documentos reales.

## Qué hace

| Paso | Detalle |
|---|---|
| Setup | Carga `OPENAI_API_KEY` desde Colab userdata o `.env`. |
| Documento | `car-inspection-form_1.png` — formulario real con manuscrito y círculos Yes/No. |
| Esquema | `FormAnswer` (Pydantic): los pares campo → valor del formulario. |
| Extracción | `ChatPromptTemplate` multimodal → `with_structured_output()` → JSON garantizado. |

La discusión final abre el siguiente nivel: **parsing agéntico de documentos**
(LlamaParse, Azure Document Intelligence) para PDFs largos, tablas y lotes.

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

## Ejecución local

```bash
# Registra el kernel de Jupyter para este entorno
uv run python -m ipykernel install --user \
  --name clase-5-3-l4 --display-name "Python (clase 5.3 · L4)"

# Abre el notebook
uv run --with jupyterlab jupyter lab ocr_semantico.ipynb
```

## Referencias

- https://docs.langchain.com/oss/python/langchain/structured-output
- https://platform.openai.com/docs/guides/images-vision
