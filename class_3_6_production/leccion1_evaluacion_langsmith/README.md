# leccion1_evaluacion_langsmith

**Evaluación de sistemas de LLMs con LangSmith**: crea un dataset, define evaluadores
(LLM-as-judge y de referencia), combínalos en una métrica compuesta y compara dos modelos.

Primera de las tres lecciones de la Clase 3.6. Aquí la evaluación vive **dentro de LangSmith**:
subes ejemplos, corres experimentos y revisas el feedback en la plataforma.

## Qué hace

| Paso | Detalle |
|---|---|
| Dataset | Sube `ejemplos_eval.csv` como dataset `Ejemplo manu` en LangSmith (evita duplicados). |
| Cadena base | `create_basic_llm(model)` = `ChatOpenAI().with_structured_output(MathAnswer)` (salidas estructuradas nativas). |
| Evaluadores | LLM-as-judge (`chain_of_thought`, `conciseness`, `maliciousness`, `6y_suitability`) + un evaluador de referencia. |
| Métrica compuesta | `safety_alignment_score` = 0.35·conciseness + 0.35·maliciousness + 0.30·6y_suitability. |
| Comparación | Corre `evaluate(...)` sobre `gpt-4o-mini` vs `gpt-5-mini` con el auxiliar `run_experiment`. |

## Requisitos
- Python 3.12 y [uv](https://github.com/astral-sh/uv).
- Cuenta de LangSmith (API key) y credenciales de OpenAI.

## Configuración
```bash
# 1. Copia la plantilla de secretos y completa tus llaves
cp .env.example .env          # edita OPENAI_API_KEY y LANGSMITH_API_KEY

# 2. Sincroniza el entorno (crea .venv con las dependencias fijadas)
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
```
El `.env` real nunca se versiona (está en `.gitignore`). En Google Colab las llaves se leen
desde `google.colab.userdata` usando los mismos nombres.

## Ejecución local
```bash
# Registra el kernel de Jupyter para este entorno
uv run python -m ipykernel install --user \
  --name clase-3-6-l1 --display-name "Python (clase 3.6 · L1)"

# Abre el notebook
uv run --with jupyterlab jupyter lab evaluacion_de_agentes.ipynb
```
Ejecuta las celdas en orden: dependencias/variables → dataset → experimentos → resultados.
Cada run incluye el feedback `safety_alignment_score`, calculado automáticamente al cierre.

> `ejemplos_eval.csv` debe permanecer junto al notebook — el cuaderno lo lee desde el directorio actual.

## Referencias
- https://docs.langchain.com/langsmith/evaluate-llm-application
- https://docs.langchain.com/langsmith/code-evaluator
- https://docs.langchain.com/langsmith/llm-as-judge
- https://docs.langchain.com/langsmith/composite-evaluators
