# leccion5_codeact_ejecucion_de_codigo

**CodeAct: cuando la acción del agente es escribir código.** La lección enfrenta los dos patrones sobre el mismo análisis de ventas: un agente de **tool-calling puro** (`gpt-5-mini` + dos herramientas estrechas con menú fijo de operaciones) contra **Claude con el sandbox de ejecución de código de Anthropic** (`code_execution`: un contenedor gestionado y aislado donde el modelo escribe y corre Python). La mediana por grupo, la correlación y la regresión con R² están fuera del menú del primero — y a un `import pandas` del segundo.

Quinta lección de la Clase 5.4 — Integraciones. **La única de la clase que usa `ANTHROPIC_API_KEY`.**

## Qué hace

| Paso | Detalle |
|---|---|
| Primer contacto | Una llamada con la tool `code_execution_20260120` (de servidor: Anthropic la ejecuta, sin loop del lado del cliente). El helper `preguntar_sandbox()` recorre los bloques (`text`, `server_tool_use`, `bash_code_execution_tool_result`) y maneja `pause_turn` y `refusal`. |
| Datos | [`data/ventas_diarias.csv`](data/ventas_diarias.csv) (368 filas, semilla fija, [`generar_datos.py`](generar_datos.py)) sube al sandbox vía Files API + bloque `container_upload`. |
| La comparación | La misma tarea (mediana por canal, correlación nieve↔ventas, regresión con R²) para ambos agentes, con la respuesta correcta calculada en pandas como juez. El de herramientas estrechas declara honestamente su techo; el del sandbox escribe pandas. |
| Artefactos | El gráfico se genera en el sandbox y se descarga por Files API (`bash_code_execution_output` → `file_id`) a `outputs/`. |
| Estado | El `container.id` persiste entre llamadas: la pregunta de seguimiento usa los datos ya cargados. |
| Cierre | Cuándo cada patrón: verbos estrechos para *efectos*, sandbox para *cómputo*; por qué jamás un `exec()` local. |

## Requisitos

- Python 3.12 y [uv](https://github.com/astral-sh/uv), o Google Colab (la primera celda baja el CSV del repo).
- `ANTHROPIC_API_KEY` ([console.anthropic.com](https://console.anthropic.com)) para el sandbox. El modelo es parametrizable (`MODELO_CLAUDE`): por defecto `claude-opus-5`; `claude-haiku-4-5` es la opción económica para practicar. El sandbox es gratis hasta 1.550 h/mes por organización.
- `OPENAI_API_KEY` para el agente de comparación (~4 llamadas a `gpt-5-mini`).
- Sin alguna de las dos llaves, las secciones correspondientes se saltan con aviso.

## Configuración

```bash
# 1. Copia la plantilla de secretos y completa tus llaves
cp .env.example .env          # edita ANTHROPIC_API_KEY y OPENAI_API_KEY

# 2. Sincroniza el entorno (crea .venv con las dependencias fijadas)
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
```

## Ejecución local

```bash
# Registra el kernel de Jupyter para este entorno
uv run python -m ipykernel install --user \
  --name clase-5-4-l5 --display-name "Python (clase 5.4 · L5)"

# Abre el notebook
uv run --with jupyterlab jupyter lab codeact_ejecucion_de_codigo.ipynb
```

El gráfico descargado del sandbox queda en `outputs/` (git-ignorado).

## Notas

- El sandbox: Python 3.11 con pandas/numpy/matplotlib/scipy preinstalados, **sin internet**, 1 CPU / 5 GiB; los contenedores persisten 30 días y se reutilizan pasando `container=<id>`.
- `code_execution_20260120` es GA (sin beta header); la Files API sí lleva el header `files-api-2025-04-14` (el helper lo agrega con `extra_headers`).
- Las herramientas estrechas del agente de comparación son un diseño *honesto*, no un espantapájaros: `suma/promedio/max/min/contar` con groupby es lo que un backend típico expone. El punto es la pendiente del vocabulario, no la torpeza del agente.

## Referencias

- https://arxiv.org/abs/2402.01030 (CodeAct: Executable Code Actions Elicit Better LLM Agents)
- https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool
