# leccion3_capa_semantica

**Una capa semántica sobre una base de datos "heredada": lo que los datos significan, puesto en un grafo consultable.** Se crea una base SQLite mockeada de un centro de esquí (nombres crípticos, FKs sin declarar y una trampa de moneda invisible: pesos chilenos y argentinos conviviendo sin que nada lo diga), se demuestra que un LLM a ciegas responde mal, y se construye la solución por capas en Neo4j: la capa técnica con [neocarta](https://github.com/neo4j-labs/neocarta) (Neo4j Labs), la capa de negocio desde una ontología escrita a mano, y una capa de sinónimos generada por `gpt-5-mini`.

Tercera lección de la Clase 5.4 — Integraciones. La lección 4 usa este grafo para el agente SQL.

## Qué hace

| Paso | Detalle |
|---|---|
| El problema | `gpt-5-mini` con el esquema pelado: suma `trx_pos.mnt` (CLP) con `res_agt.imp` (ARS) directo, o ignora las agencias — no tiene cómo saber la moneda. |
| La base | [`crear_base_datos.py`](crear_base_datos.py): 11 tablas SQLite, ~5.400 ventas, determinística por semilla. Solo 2 FKs declaradas; 7 joins son convención. |
| Capa técnica | [`generar_metadata_csv.py`](generar_metadata_csv.py) introspecta con `PRAGMA` y escribe los CSVs del conector de neocarta → `(:Database)→(:Schema)→(:Table)→(:Column)→(:Value)` + glosario. |
| Capa de negocio | [`ontologia.yaml`](ontologia.yaml) + [`construir_capa_negocio.py`](construir_capa_negocio.py): dominios, métricas, **monedas por declaración explícita**, joins por convención. Idempotente, con procedencia (`source`) por arista. |
| El recorrido | Las consultas que el grafo responde: mapa por dominio, alineación por métrica, la trampa CLP/ARS desarmada, joins listos para SQL, glosario, y el grafo dibujado (networkx). |
| Enriquecimiento LLM | Sinónimos en español por tabla (`llm_sinonimos`), y búsqueda en el idioma del negocio. |

## Requisitos

- Python 3.12 y [uv](https://github.com/astral-sh/uv), o Google Colab (la primera celda baja los scripts del repo).
- **Neo4j** — dos caminos:
  - Local (recomendado): Docker y `docker run -d --name neo4j-clase54 -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:5`
  - Colab / sin Docker: una instancia gratis de [Neo4j Aura](https://console.neo4j.io) (URI `neo4j+s://…` en el `.env` o en los secrets de Colab).
  - Sin Neo4j el notebook corre igual: las celdas de grafo se saltan con aviso.
- `OPENAI_API_KEY` — opcional: solo para la demo del problema y el enriquecimiento (≈12 llamadas a `gpt-5-mini`; costo despreciable).

> ⚠️ Si ya usas Neo4j para otra cosa, dale a la lección su propio contenedor o instancia: la lección escribe (y la lección 4 **borra y reconstruye**) el grafo completo de la base a la que se conecta.

## Configuración

```bash
# 1. Copia la plantilla de secretos y ajusta la conexión / llave
cp .env.example .env          # edita NEO4J_* y (opcional) OPENAI_API_KEY

# 2. Sincroniza el entorno (crea .venv con las dependencias fijadas)
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
```

## Ejecución local

```bash
# Registra el kernel de Jupyter para este entorno
uv run python -m ipykernel install --user \
  --name clase-5-4-l3 --display-name "Python (clase 5.4 · L3)"

# Abre el notebook
uv run --with jupyterlab jupyter lab capa_semantica_grafos.ipynb
```

La base (`montania.db`), los CSVs de metadata y el grafo dibujado quedan en `outputs/` (git-ignorado). El grafo queda en Neo4j — la lección 4 lo espera ahí (y si no está, lo reconstruye sola). Para explorarlo a mano: `http://localhost:7474` (Neo4j Browser).

## Nota sobre el diseño

- La moneda de cada columna es **declaración explícita en la ontología**, no un sufijo del nombre ni una cuestión de magnitudes: en versiones anteriores los nombres (`mnt_clp`/`mnt_usd`) o los tamaños de los montos (USD chicos vs CLP grandes) delataban la moneda y el modelo adivinaba bien. Con pesos argentinos los montos son indistinguibles y el conocimiento es 100% tribal — como en los esquemas reales.
- neocarta no tiene conector SQLite: el camino es introspección → CSVs normalizados → `CSVConnector`. El mismo patrón sirve para cualquier fuente sin conector.
- El vector search / búsqueda híbrida de neocarta (`neocarta[mcp]`) queda como frontera: acá los sinónimos se buscan con `CONTAINS` para que se vea el mecanismo.

## Referencias

- https://github.com/neo4j-labs/neocarta
- https://neo4j.com/docs/getting-started/cypher-intro/
- https://neo4j.com/aura/ (tier gratuito)
