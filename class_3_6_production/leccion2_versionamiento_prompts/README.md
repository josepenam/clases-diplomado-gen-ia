# leccion2_versionamiento_prompts

**Versionamiento y mantenimiento de prompts** con el Prompt Hub de LangSmith: descarga
prompts publicados, fíjalos a una versión concreta y reejecútalos dentro de una cadena.

Segunda de las tres lecciones de la Clase 3.6. Muestra cómo tratar los prompts como
artefactos versionados en lugar de strings incrustados en el código.

## Qué hace

| Caso | Detalle |
|---|---|
| Prompt público | `client.pull_prompt("hardkothari/blog-generator", include_model=True)` y lo corre sobre `ai_news.txt`. |
| Prompt propio | Descarga `profe-blog-enerator` y una versión fijada `profe-blog-enerator:25fb38a3`. |
| Cadena | Alimenta el prompt a `ChatOpenAI('gpt-5-mini')` y compara salidas entre versiones. |

## Requisitos
- Python 3.12 y [uv](https://github.com/astral-sh/uv).
- Cuenta de LangSmith (API key) y credenciales de OpenAI.

## Configuración
```bash
cp .env.example .env          # edita OPENAI_API_KEY y LANGSMITH_API_KEY
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
```
> El notebook lee la credencial de LangSmith desde `LANGSMITH_API_KEY` (nombre estándar del SDK).

El `.env` real nunca se versiona. En Google Colab las llaves se leen desde `google.colab.userdata`.

## Ejecución local
```bash
uv run python -m ipykernel install --user \
  --name clase-3-6-l2 --display-name "Python (clase 3.6 · L2)"

uv run --with jupyterlab jupyter lab versionamiento_de_prompts.ipynb
```
> `ai_news.txt` debe permanecer junto al notebook — es la entrada de la cadena.

## Referencias
- https://docs.langchain.com/langsmith/manage-prompts
- https://docs.smith.langchain.com/prompt_engineering/how_to_guides
