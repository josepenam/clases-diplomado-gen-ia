# leccion4_agente_sql_semantico

**El capstone de la dupla semántica: un agente que primero entiende y después calcula.** `create_agent` (LangChain 1.x) + `gpt-5-mini` con dos herramientas de solo lectura — `leer_cypher` sobre la capa semántica de la lección 3 y `ejecutar_sql` sobre la base SQLite — y el método DESCUBRIR → VERIFICAR → CALCULAR → EXPLICAR en el prompt. El corazón es el contraste medido: la misma pregunta con trampa de moneda a un agente *a ciegas* (solo SQL + esquema pelado) y al agente *informado*, con la respuesta correcta calculada aparte como juez.

Cuarta lección de la Clase 5.4 — Integraciones. Autocontenida: no requiere haber corrido la lección 3.

## Qué hace

| Paso | Detalle |
|---|---|
| El mundo | [`construir_grafo.py`](construir_grafo.py) reconstruye base + grafo desde cero, idempotente, con guardia (solo borra grafos vacíos o creados por esta clase). |
| Las guardas | `leer_cypher` corre en `execute_read` (las escrituras fallan estructuralmente); `ejecutar_sql` valida el texto **y** abre SQLite `mode=ro`. Se ven rechazar un `DROP` en vivo. |
| El agente | El método del analista senior en el system prompt; reglas duras de moneda y período. |
| El contraste | *"¿Facturación total de julio, incluyendo agencias, en pesos chilenos?"* — `res_agt.imp` está en pesos **argentinos** (magnitudes indistinguibles de CLP) y solo el grafo lo sabe. El a ciegas fabrica un número; el informado descubre `IN_CURRENCY → ARS`, encuentra `tc_d` y convierte. Tabla de veredictos con la respuesta correcta (pandas) como juez. |
| El recorrido | El subgrafo que el agente caminó, dibujado con el número de paso en cada tabla (networkx). |

## Requisitos

- Python 3.12 y [uv](https://github.com/astral-sh/uv), o Google Colab (la primera celda baja los scripts del repo).
- **Neo4j** (igual que la lección 3): Docker local `docker run -d --name neo4j-clase54 -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:5`, o Aura Free para Colab.
- `OPENAI_API_KEY` — las corridas de los dos agentes usan `gpt-5-mini` (~15–25 llamadas en total; costo bajo).
- Sin Neo4j o sin llave, las celdas de agente se saltan (la base y el juez con pandas corren igual).

> ⚠️ `construir_grafo.py` **borra y reconstruye** el grafo de la base a la que apunta `NEO4J_URI`. La guardia aborta si encuentra un grafo que esta clase no creó — dale a la lección su propio contenedor.

## Configuración

```bash
# 1. Copia la plantilla de secretos y completa llave y conexión
cp .env.example .env          # edita OPENAI_API_KEY y NEO4J_*

# 2. Sincroniza el entorno (crea .venv con las dependencias fijadas)
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
```

## Ejecución local

```bash
# Registra el kernel de Jupyter para este entorno
uv run python -m ipykernel install --user \
  --name clase-5-4-l4 --display-name "Python (clase 5.4 · L4)"

# Abre el notebook
uv run --with jupyterlab jupyter lab agente_sql_semantico.ipynb
```

## Notas

- Los agentes no son deterministas: los caminos (y el número de tool calls) varían entre corridas. Lo que no varía es la asimetría: el a ciegas *no puede* saber la moneda de `imp`; el informado la consulta. `correr()` reintenta una vez si un agente se enreda y agota los pasos.
- La trampa está endurecida a propósito: en una versión anterior las reservas estaban en USD y el modelo a ciegas a veces acertaba, porque las magnitudes (~300 vs ~65.000) delataban la moneda. En ARS los montos son indistinguibles de CLP.
- `crear_base_datos.py`, `ontologia.yaml` y compañía son copias de la lección 3 (convención de autocontención del repo): si cambias una, sincroniza la otra.
- Esta lección es la adaptación docente de un agente real sobre un data lake corporativo con BigQuery y el SDK de agentes de Anthropic; el patrón dos-herramientas-un-método es el mismo.

## Referencias

- https://docs.langchain.com/oss/python/langchain/agents
- https://github.com/neo4j-labs/neocarta
