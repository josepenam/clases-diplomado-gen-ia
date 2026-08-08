# leccion1_mcp

**MCP (Model Context Protocol): el protocolo abierto para conectar LLMs con herramientas, datos y plantillas.** Se construyen dos servidores FastMCP que simulan sistemas de un centro de esquí (ventas y meteorología), se descubren sus capacidades desde un cliente que no sabe nada de ellos, y se conecta un agente de LangChain que responde preguntas reales llamando a las tools por el protocolo.

Primera lección de la Clase 5.4 — Integraciones.

## Qué hace

| Paso | Detalle |
|---|---|
| Anatomía | Un servidor FastMCP de juguete definido en celda: tools, un resource y los esquemas que el cliente ve. |
| Servidores reales | [`servidor_transacciones.py`](servidor_transacciones.py) y [`servidor_pronostico_nieve.py`](servidor_pronostico_nieve.py): salida estructurada (Pydantic), resources estáticos y dinámicos, prompts, y logging/progreso vía `ctx`. |
| Ciclo de vida | Los servidores se lanzan como procesos (`subprocess.Popen`), se espera el puerto, y la última celda los termina. |
| Descubrimiento | `MultiServerMCPClient` lista tools, lee resources (estático y por plantilla de URI) e invoca prompts. |
| El agente | `create_agent` (LangChain 1.x) + `gpt-5-mini` conectado a los dos servidores. **El contraste medido**: la misma pregunta sin tools (el modelo se declara ignorante) y con MCP (1 llamada, datos concretos). |
| Transportes | streamable-http vs stdio, y cuándo usar cada uno. |

## Requisitos

- Python 3.12 y [uv](https://github.com/astral-sh/uv), o Google Colab (la primera celda baja los `.py` de los servidores desde el repo).
- `OPENAI_API_KEY` ([platform.openai.com](https://platform.openai.com)) — solo para la sección del agente; los servidores y el cliente MCP funcionan sin llave. El costo de las llamadas es despreciable: unas pocas consultas con `gpt-5-mini`.

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
  --name clase-5-4-l1 --display-name "Python (clase 5.4 · L1)"

# Abre el notebook
uv run --with jupyterlab jupyter lab protocolo_mcp.ipynb
```

Los servidores usan los puertos **8801** y **8802** (configurables con `MCP_PORT_TRANSACCIONES` / `MCP_PORT_PRONOSTICO`). Si el notebook muere sin correr la celda de limpieza, el `atexit` registrado los termina; en el peor caso: `pkill -f servidor_`.

Para inspeccionar un servidor a mano, el SDK trae una UI: `uv run mcp dev servidor_pronostico_nieve.py` y abrir `http://127.0.0.1:6274`.

## Nota sobre versiones

- El material usaba `create_react_agent` de `langgraph.prebuilt` (pre-1.0) y `gpt-4.1`; ahora usa **`create_agent` de LangChain 1.x** y `gpt-5-mini`.
- Está fijado **`mcp==1.29.0`** a propósito: el SDK v2 ya existe, pero `langchain-mcp-adapters` requiere la serie 1.x. El protocolo es el mismo.
- Los argumentos de un *prompt* MCP viajan como strings por protocolo (el servidor los convierte); los parámetros de una *URI template* van en el path, donde una URL tolera espacios.

## Referencias

- https://modelcontextprotocol.io
- https://github.com/modelcontextprotocol/python-sdk
- https://github.com/langchain-ai/langchain-mcp-adapters
