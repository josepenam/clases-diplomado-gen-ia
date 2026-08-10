# Módulo 5 · Clase 4 — Integraciones

Diplomado de Extensión en IA Generativa para Organizaciones.

Un LLM aislado solo puede conversar. Esta clase lo conecta con todo lo que no es el LLM: herramientas y servicios (MCP), el conocimiento operativo del equipo (skills), los datos de la empresa (capas semánticas y un agente SQL), cómputo real (ejecución de código en sandbox) y datos visuales (un test de multimodalidad).

**El hilo conductor: cada lección mide el contraste con y sin la integración.** El mismo agente con y sin herramientas MCP, la misma tarea con y sin skill, la misma pregunta de negocio con y sin capa semántica, el mismo análisis por tool-calling puro y por código. La integración no se declara: se demuestra con el delta.

---

## Objetivos de aprendizaje

Al terminar la clase, un estudiante puede:

1. Explicar qué problema resuelve **MCP** (N×M adaptadores → un protocolo) y qué controla cada bloque: tools el modelo, resources la aplicación, prompts el usuario.
2. Construir un servidor **FastMCP** con salida estructurada, resources por URI y logging/progreso vía `ctx`, y conectarle un agente que descubre sus capacidades por protocolo.
3. Escribir una **skill** (SKILL.md del estándar abierto) con una `description` que dispare bien, y explicar el *progressive disclosure* implementándolo en ~30 líneas.
4. Distribuir una skill a varios agentes (Claude Code, Cursor) desde un playbook central con **Packmind** — y explicar qué hace la herramienta por dentro.
5. Argumentar por qué un esquema SQL no basta para text-to-SQL confiable, y qué agrega una **capa semántica**: dominios, métricas, monedas explícitas y joins por convención.
6. Construir esa capa en **Neo4j** por capas con procedencia (técnica con neocarta, negocio con una ontología, sinónimos con LLM).
7. Armar un **agente SQL semántico** con herramientas de solo lectura estructuralmente incapaces de escribir, y el método DESCUBRIR → VERIFICAR → CALCULAR → EXPLICAR.
8. Decidir entre **tool-calling y CodeAct** según la tarea (efectos vs cómputo), y usar el sandbox gestionado de Anthropic sin ejecutar jamás código del modelo en la propia máquina.
9. Diseñar experimentos con **juez imparcial**: la respuesta correcta calculada aparte, veredictos programáticos, tolerancias honestas.
10. Elegir dónde vive cada credencial y **nunca** versionar un `.env` real.

## Prerrequisitos

- Python 3.12 y [uv](https://github.com/astral-sh/uv) (`brew install uv`), o Google Colab.
- `OPENAI_API_KEY` ([platform.openai.com](https://platform.openai.com)) — todas las lecciones; el gasto total de la clase es bajo (mayormente `gpt-5-mini` / `nano`).
- `ANTHROPIC_API_KEY` ([console.anthropic.com](https://console.anthropic.com)) — **solo la lección 5** (el sandbox de código).
- **Docker** para Neo4j local (lecciones 3–4): `docker run -d --name neo4j-clase54 -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:5`. Alternativa sin Docker (y para Colab): una instancia gratis de [Neo4j Aura](https://console.neo4j.io).
- **Node ≥ 20** — opcional, para la CLI de Packmind en la lección 2 (que además pide cuenta en [app.packmind.com](https://app.packmind.com), gratis; sin nada de esto el fallback local enseña lo mismo).
- **Un motor LaTeX** para la lección 6: `brew install tectonic` (o MacTeX si ya está); en Colab, `apt-get install texlive-latex-extra`.

> **Colab o local:** todas las lecciones corren en Colab (la primera celda de cada notebook baja del repo los archivos que necesita y trae el `%pip install` comentado con los pins exactos). Local con uv es la experiencia recomendada: entornos reproducibles por lección.

> **Degradación:** cada notebook corre de punta a punta aunque falten llaves o servicios — las celdas afectadas se saltan con un aviso claro. Lo único imprescindible por lección está en su README.

---

## Estructura del proyecto

```
class_5_4_integraciones/
├── README.md                            ← este archivo
├── deck/deck_5_4_integraciones.pptx     ← diapositivas de la clase
├── data/            outputs/            ← convención del repo (vacíos)
├── leccion1_mcp/                        ← MCP: protocolo, servidores y agente
│   ├── protocolo_mcp.ipynb
│   └── servidor_transacciones.py · servidor_pronostico_nieve.py
├── leccion2_skills_y_gestion/           ← skills: estándar, mecanismo, Packmind
│   ├── skills_y_gestion_de_skills.ipynb
│   └── skills/{informe-nieve,aviso-cierre-pistas,respuesta-reclamos}/SKILL.md
├── leccion3_capa_semantica/             ← ontologías y grafos: SQLite → neocarta → Neo4j
│   ├── capa_semantica_grafos.ipynb
│   └── crear_base_datos.py · generar_metadata_csv.py · construir_capa_negocio.py · ontologia.yaml
├── leccion4_agente_sql_semantico/       ← capstone: el agente informado por el grafo
│   ├── agente_sql_semantico.ipynb
│   └── construir_grafo.py (+ copias autocontenidas de los scripts de L3)
├── leccion5_codeact_ejecucion_de_codigo/ ← CodeAct: sandbox de Anthropic vs tool-calling
│   ├── codeact_ejecucion_de_codigo.ipynb
│   └── data/ventas_diarias.csv · generar_datos.py
└── leccion6_test_multimodalidad/        ← dibujar a ciegas: el test del unicornio
    └── test_de_multimodalidad.ipynb
```

Cada lección es **autocontenida**: su propio `README`, su entorno `uv` (`pyproject.toml` + `uv.lock`), su `.gitignore` y su `.env.example`. Cada una corresponde a un tramo del deck.

### Lección 1 — `leccion1_mcp/` *(deck: sección MCP)*

Dos servidores FastMCP mock de Valle Nevado (transacciones y pronóstico de nieve) con tools tipadas, resources estáticos y dinámicos, prompts, y logging/progreso reales por `ctx`. Un cliente que descubre capacidades sin conocer los servidores, y un agente LangChain 1.x que responde con datos lo que sin tools solo podía adivinar.

```bash
cd leccion1_mcp
cp .env.example .env                       # OPENAI_API_KEY
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
uv run --with jupyterlab jupyter lab protocolo_mcp.ipynb
```

### Lección 2 — `leccion2_skills_y_gestion/` *(deck: sección Skills)*

El estándar abierto SKILL.md por dentro: un skill-loader de ~30 líneas sobre la API cruda de OpenAI, el contraste con/sin skill verificado programáticamente, la cuenta de tokens honesta, y la distribución multi-agente con Packmind (con fallback casero que enseña el mecanismo). Se diferencia explícitamente de la clase 3.6 L3 (versionado).

```bash
cd leccion2_skills_y_gestion
cp .env.example .env                       # OPENAI_API_KEY (+ PACKMIND_API_KEY_V3 opcional)
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
uv run --with jupyterlab jupyter lab skills_y_gestion_de_skills.ipynb
```

### Lección 3 — `leccion3_capa_semantica/` *(deck: sección Capas semánticas)*

Una base SQLite "heredada" (11 tablas crípticas, 2 FKs de 9 joins reales, y la trampa: pesos chilenos y argentinos conviviendo sin que nada lo diga) y la capa semántica que la vuelve consultable: técnica (neocarta), negocio (ontología) y sinónimos (LLM), con procedencia por arista.

```bash
cd leccion3_capa_semantica
cp .env.example .env                       # NEO4J_* (+ OPENAI_API_KEY opcional)
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
uv run --with jupyterlab jupyter lab capa_semantica_grafos.ipynb
```

### Lección 4 — `leccion4_agente_sql_semantico/` *(deck: sección Capas semánticas, cierre)*

El capstone: `create_agent` + `gpt-5-mini` con `leer_cypher` y `ejecutar_sql` (solo lectura, con guardas estructurales) y el método del analista senior. El agente a ciegas fabrica un total que no existe; el informado descubre la moneda en el grafo y convierte — con la respuesta de pandas como juez, y el recorrido del agente dibujado al final.

```bash
cd leccion4_agente_sql_semantico
cp .env.example .env                       # OPENAI_API_KEY + NEO4J_*
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
uv run --with jupyterlab jupyter lab agente_sql_semantico.ipynb
```

### Lección 5 — `leccion5_codeact_ejecucion_de_codigo/` *(deck: sección CodeAct)*

Code-as-actions con el sandbox gestionado de Anthropic (`code_execution`): CSV por Files API, artefactos de vuelta, contenedor persistente. El mismo análisis (mediana por canal, correlación, regresión con R²) para un agente de tool-calling con menú fijo — que declara su techo — y para Claude escribiendo pandas.

```bash
cd leccion5_codeact_ejecucion_de_codigo
cp .env.example .env                       # ANTHROPIC_API_KEY + OPENAI_API_KEY
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
uv run --with jupyterlab jupyter lab codeact_ejecucion_de_codigo.ipynb
```

### Lección 6 — `leccion6_test_multimodalidad/` *(deck: La prueba del Unicornio)*

El test de *Sparks of AGI* con los modelos de hoy: 3 modelos × 4 dibujos en TikZ, compilados (los fracasos también son dato), rasterizados y puntuados por un juez con visión. Texto → código → imagen → juicio visual.

```bash
cd leccion6_test_multimodalidad
cp .env.example .env                       # OPENAI_API_KEY
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
uv run --with jupyterlab jupyter lab test_de_multimodalidad.ipynb
```

---

## Entornos

| Lección | Manager / Python | Dependencias clave |
|---|---|---|
| L1 | **uv** · `>=3.12,<3.13` | `mcp==1.29.0` · `langchain-mcp-adapters==0.3.2` · `langchain==1.3.14` · `langchain-openai==1.4.2` |
| L2 | **uv** · `>=3.12,<3.13` | `openai==2.53.0` · `pyyaml==6.0.3` (+ Node ≥ 20 para `npx @packmind/cli`) |
| L3 | **uv** · `>=3.12,<3.13` | `neocarta==0.8.0` · `neo4j==6.2.0` · `pandas==2.3.3` · `networkx==3.6.1` |
| L4 | **uv** · `>=3.12,<3.13` | `langchain==1.3.14` · `neocarta==0.8.0` · `neo4j==6.2.0` · `matplotlib==3.11.1` |
| L5 | **uv** · `>=3.12,<3.13` | `anthropic==0.121.0` · `langchain==1.3.14` · `pandas==2.3.3` |
| L6 | **uv** · `>=3.12,<3.13` | `openai==2.53.0` · `pymupdf==1.28.2` (+ tectonic o pdflatex) |

Los `requirements.txt` de cada lección espejan los pins exactos para el camino Colab. Kernels: `clase-5-4-lN` con display name `"Python (clase 5.4 · LN)"`.

## Secrets

Never commit a real `.env`. Cada lección trae su `.env.example`; la copia real vive solo en tu máquina (los `.gitignore` de lección y raíz la excluyen). En Colab usa el gestor de secretos (`userdata`) — las primeras celdas lo leen solas. Las llaves por lección: `OPENAI_API_KEY` (todas), `ANTHROPIC_API_KEY` (solo L5), `NEO4J_*` (L3–L4), `PACKMIND_API_KEY_V3` (L2, opcional).

Todas las lecciones cargan con `load_dotenv(override=True)`, a propósito: si tu editor o tu shell ya exporta una de estas variables (una `ANTHROPIC_API_KEY` de otro proyecto, un `NEO4J_URI` que apunta a otro servidor), sin `override` esa variable heredada gana y el notebook falla con un `401` o se conecta a la base equivocada — con el `.env` correcto delante de tus ojos. Si algo así te pasa, `import os; os.environ["LA_VARIABLE"][:12]` te dice qué llave está usando de verdad.

## Nota sobre modelos y APIs

| El material usaba | Ahora usa | Por qué |
|---|---|---|
| `create_react_agent` (langgraph.prebuilt, pre-1.0) | `create_agent` (LangChain 1.x) | El par viejo quedó deprecado; el grafo se invoca con `{"messages": [...]}`. |
| `openai:gpt-4.1` | `gpt-5-mini` (agentes) / `gpt-5.5`–`gpt-5-nano` (benchmark L6) | Lineup vigente; los minis bastan para las tareas de clase. |
| SDK `mcp` sin pin | `mcp==1.29.0` **a propósito** | El SDK v2 ya existe, pero `langchain-mcp-adapters` requiere la serie 1.x. |
| — | `code_execution_20260120` (Anthropic, GA) | El sandbox gestionado que hace posible CodeAct sin ejecutar código del modelo localmente. |
| `pdflatex` + `pdftocairo` (poppler) | tectonic **o** pdflatex + PyMuPDF | Una dependencia de sistema menos para el render de L6. |
