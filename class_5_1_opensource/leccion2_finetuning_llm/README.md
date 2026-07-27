# leccion2_finetuning_llm

**Fine-tuning completo de un LLM pequeño con Hugging Face**: adapta DistilGPT2 (82M
parámetros) a WikiText-2 con la API `Trainer`, entendiendo cada pieza — tokenización, data
collator, argumentos de entrenamiento y el bucle de fine-tuning.

Segunda de las tres lecciones de la Clase 5.1. La demo entrena sobre un **subset de 2.000
ejemplos** para terminar en minutos; la teoría del deck se acompaña con el demo interactivo
de descenso de gradiente ([`../deck/gradient_descent.html`](../deck/gradient_descent.html)).

## Qué hace

| Paso | Detalle |
|---|---|
| Dataset | `Salesforce/wikitext` (`wikitext-2-raw-v1`), filtrado y submuestreado (2.000 train / 200 val). |
| Modelo | `distilgpt2` (82M parámetros), tokenizador GPT-2 con `pad_token = eos_token`. |
| Collator | `DataCollatorForLanguageModeling(mlm=False)` — predicción del siguiente token. |
| Entrenamiento | `Trainer` (transformers v5, `processing_class=`), 1 época ≈ 250 pasos, batch efectivo 8 en cuda/mps/cpu. |
| Evaluación | Generación con prompts en inglés + comparación contra el modelo original. |
| Guardado | `outputs/distilgpt2-finetuneado-demo/` (git-ignorado, formato safetensors). |

> El modelo y el corpus están **en inglés**, así que la evaluación es en inglés — el notebook
> explica por qué (los datos definen la lengua y el dominio del modelo).

## Requisitos

- Python 3.12 y [uv](https://github.com/astral-sh/uv), **o** Google Colab con GPU (T4).
- **Sin API keys**: modelo y dataset son públicos (no requiere `HF_TOKEN`; solo haría falta
  para modelos gateados, que no es el caso).
- Descargas en runtime: DistilGPT2 (~353 MB) + WikiText-2 (~5 MB) desde Hugging Face Hub.

### Tiempo de ejecución esperado

| Hardware | Tiempo total |
|---|---|
| Colab GPU T4 | ~3–6 min |
| Apple Silicon (MPS) | ~5–10 min |
| CPU | ~25–40 min (no recomendado — usa Colab) |

## Configuración

```bash
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
```

En Colab no necesitas nada de esto: la primera celda del notebook instala las dependencias
fijadas (reutilizando el `torch` preinstalado de Colab). Activa un runtime con GPU
(Entorno de ejecución → Cambiar tipo de entorno de ejecución → T4).

## Ejecución local

```bash
# Registra el kernel de Jupyter para este entorno
uv run python -m ipykernel install --user \
  --name clase-5-1-l2 --display-name "Python (clase 5.1 · L2)"

# Abre el notebook
uv run --with jupyterlab jupyter lab finetuning_llm.ipynb
```

Todo lo que genera el entrenamiento (checkpoints y modelo final) vive en `outputs/`, que está
git-ignorado.

## Referencias

- https://huggingface.co/distilbert/distilgpt2
- https://huggingface.co/datasets/Salesforce/wikitext
- https://huggingface.co/docs/transformers/training
- https://huggingface.co/docs/transformers/main_classes/trainer
