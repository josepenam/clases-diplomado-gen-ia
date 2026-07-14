"""
Lección 3 — a Claude Managed Agent: the "Analista Económico Chile".

Instead of serving a model ourselves (lección 2), we let Anthropic host the whole
agent: the platform runs the agent loop (the "brain") and a cloud sandbox (the
"hands"), and every conversation lives in a durable, server-side **session**
(an append-only event log). Building it takes three API calls:

    environments.create  →  agents.create  →  sessions.create

This module provisions the agent once (ids cached in `agent_config.json`) and
exposes the small session helpers the class notebook uses:
`Test_managed_agent_sessions.ipynb` at the class root.

Requires an ANTHROPIC_API_KEY with Managed Agents (beta) access.
"""
import json
import os
from pathlib import Path

import anthropic
from dotenv import dotenv_values

# LangSmith es opcional: si no está instalado (o el tracing está apagado) el
# agente funciona igual. `traceable` se vuelve un decorador no-op.
try:
    from langsmith import traceable
    from langsmith.run_helpers import get_current_run_tree
except Exception:  # pragma: no cover - langsmith no instalado
    def traceable(*d_args, **d_kwargs):
        if len(d_args) == 1 and callable(d_args[0]) and not d_kwargs:
            return d_args[0]  # uso como @traceable sin paréntesis

        def _decorator(func):
            return func

        return _decorator

    def get_current_run_tree():
        return None

HERE = Path(__file__).parent


def _resolve_api_key() -> str | None:
    """Prefer a real key from a local .env (lesson folder, then class root),
    and fall back to the ANTHROPIC_API_KEY already in the environment.

    We read the file explicitly (dotenv_values) instead of load_dotenv() on
    purpose: a stale ANTHROPIC_API_KEY in your shell / VS Code environment would
    otherwise shadow the .env, because load_dotenv() never overrides an existing
    variable. Reading the file and passing the key to the client makes the .env win.
    """
    for env_path in (HERE / ".env", HERE.parent / ".env"):
        if env_path.exists():
            key = (dotenv_values(env_path).get("ANTHROPIC_API_KEY") or "").strip()
            if key and "your-" not in key:  # ignore the .env.example placeholder
                return key
    return os.getenv("ANTHROPIC_API_KEY")


client = anthropic.Anthropic(api_key=_resolve_api_key())

MODEL = "claude-sonnet-5"  # the workshop used Opus; Sonnet is plenty (and cheaper) for class
MANAGED_AGENTS_BETA = "managed-agents-2026-04-01"  # header for session-scoped file listing/download
CONFIG_FILE = HERE / "agent_config.json"
OUTPUTS_DIR = HERE.parent / "outputs"

SYSTEM = """\
Eres el "Analista Económico Chile": un agente que responde preguntas sobre la
economía chilena con datos duros y contexto.

Datos duros: consúltalos SIEMPRE ejecutando Python en tu sandbox contra la API
pública mindicador.cl (gratuita, sin API key):
  - https://mindicador.cl/api                    → todos los indicadores de hoy
  - https://mindicador.cl/api/{indicador}        → serie reciente del indicador
  - https://mindicador.cl/api/{indicador}/{año}  → serie de un año (ej: /uf/2025)
  Indicadores: uf, dolar, euro, utm, ipc, tpm, imacec, tasa_desempleo, bitcoin.

Contexto más amplio (noticias, causas, análisis): usa web_search / web_fetch y
cita tus fuentes.

Cuando te pidan un informe, escríbelo en /mnt/session/outputs/ (markdown) para
que el cliente pueda descargarlo. Responde siempre en español, conciso y con cifras.
"""

# Built-in toolset: code execution in the sandbox, plus web_search/web_fetch for
# broader context (the platform runs those outside the sandbox, so the
# environment's host allowlist below does not apply to them).
TOOLS = [
    {
        "type": "agent_toolset_20260401",
        "default_config": {"enabled": True},
        "configs": [
            {"name": "web_search", "enabled": True},
            {"name": "web_fetch", "enabled": True},
        ],
    },
]

# The sandbox can only reach mindicador.cl (plus package managers to pip-install).
ENVIRONMENT_CONFIG = {
    "type": "cloud",
    "networking": {
        "type": "limited",
        "allowed_hosts": ["mindicador.cl"],
        "allow_package_managers": True,
    },
    "packages": {"type": "packages", "pip": ["requests", "pandas", "matplotlib"]},
}


# ── Provisioning (run once): environment + agent ─────────────────────────────
def setup_environment() -> str:
    env = client.beta.environments.create(
        name="analista-economico-cl-env", config=ENVIRONMENT_CONFIG,
    )
    return env.id


def setup_agent() -> str:
    agent = client.beta.agents.create(
        name="Analista Económico Chile", model=MODEL, system=SYSTEM, tools=TOOLS,
    )
    return agent.id


def provision() -> dict:
    """Create the environment + agent once; later calls reuse the cached ids."""
    if CONFIG_FILE.exists():
        cfg = json.loads(CONFIG_FILE.read_text())
        print(f"Reusing existing agent ({CONFIG_FILE.name}): {cfg['agent_id']}")
        return cfg
    cfg = {
        "environment_id": setup_environment(),
        "agent_id": setup_agent(),
        "model": MODEL,
    }
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2) + "\n")
    print(f"Provisioned agent {cfg['agent_id']} + environment {cfg['environment_id']}")
    return cfg


# ── Sessions: create, talk, resume, download, delete ─────────────────────────
def start_session(agent_id: str, env_id: str, title: str = "Consulta económica") -> str:
    session = client.beta.sessions.create(
        agent=agent_id, environment_id=env_id, title=title,
    )
    return session.id


def send_and_stream(session_id: str, user_text: str):
    """Send a user message and yield the session's events until the turn ends."""
    with client.beta.sessions.events.stream(session_id) as stream:
        client.beta.sessions.events.send(
            session_id,
            events=[{"type": "user.message", "content": [{"type": "text", "text": user_text}]}],
        )
        for ev in stream:
            yield ev
            if ev.type == "session.status_idle":
                break


def print_reply(session_id: str, user_text: str) -> str:
    """Notebook convenience: send a message, pretty-print activity, return the text."""
    buf = ""
    for ev in send_and_stream(session_id, user_text):
        if ev.type == "agent.message":
            text = _text(ev.content)
            buf += text
            print(text, end="", flush=True)
        elif ev.type == "agent.tool_use":
            print(f"\n⚙️  [sandbox · {ev.name}]", flush=True)
    print()
    return buf


def list_sessions(agent_id: str) -> list:
    page = client.beta.sessions.list(agent_id=agent_id, limit=20, order="desc")
    return list(page.data)


def load_history(session_id: str) -> list[tuple[str, str]]:
    """Replay a conversation from the server-side event log (the session IS the state)."""
    hist: list[tuple[str, str]] = []
    for ev in client.beta.sessions.events.list(session_id, order="asc", limit=500).data:
        if ev.type == "user.message":
            hist.append(("user", _text(ev.content)))
        elif ev.type == "agent.message":
            if hist and hist[-1][0] == "agent":
                hist[-1] = ("agent", hist[-1][1] + _text(ev.content))
            else:
                hist.append(("agent", _text(ev.content)))
        elif ev.type == "agent.tool_use":
            hist.append(("tool", ev.name))
    return hist


def download_outputs(session_id: str, dest: Path = OUTPUTS_DIR) -> list[Path]:
    """Download whatever the agent wrote to /mnt/session/outputs/.

    Session files are scoped with `scope_id`, which requires the managed-agents
    beta header — without it the API rejects `scope_id` as an unknown field.
    """
    dest.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []
    page = client.beta.files.list(scope_id=session_id, betas=[MANAGED_AGENTS_BETA])
    for f in page.data:
        if not getattr(f, "downloadable", True):
            continue
        name = getattr(f, "filename", None) or f.id
        target = dest / Path(name).name
        content = client.beta.files.download(f.id, betas=[MANAGED_AGENTS_BETA])
        if hasattr(content, "write_to_file"):
            content.write_to_file(target)
        else:
            target.write_bytes(content.read())
        saved.append(target)
    return saved


def delete_session(session_id: str) -> None:
    client.beta.sessions.delete(session_id)


def _text(content) -> str:
    if not content:
        return ""
    return "".join(getattr(b, "text", "") for b in content if getattr(b, "type", None) == "text")


# ── Tracing con LangSmith → base para correr evals ───────────────────────────
def _attach_run_metadata(**kwargs) -> None:
    """Cuelga metadata (session_id, tool_calls, model…) del run traceado actual.

    No-op si LangSmith no está activo. La metadata queda visible en cada run de
    LangSmith y sirve para filtrar/segmentar experimentos.
    """
    try:
        run = get_current_run_tree()
        if run is not None:
            run.metadata.update({k: v for k, v in kwargs.items() if v is not None})
    except Exception:  # pragma: no cover - nunca romper la corrida por el tracing
        pass


@traceable(run_type="chain", name="ask_agent")
def ask_agent(
    question: str,
    *,
    agent_id: str | None = None,
    environment_id: str | None = None,
    title: str = "Eval turn",
    cleanup: bool = True,
) -> dict:
    """Una sola pregunta contra el agente, en una **sesión nueva y aislada**.

    A diferencia de `print_reply` (que conversa sobre una sesión de larga vida),
    cada llamada abre su propia sesión: los turnos son independientes, que es la
    base correcta para evaluar (un ejemplo no contamina a otro).

    Decorada con `@traceable`, por lo que cada llamada aparece como un run en tu
    proyecto de LangSmith (con la pregunta como input y el dict de salida como
    output). Ese mismo dict es el que espera `langsmith.evaluate` como target.

    Devuelve `{"output": <texto>, "tool_calls": [...], "session_id": ...}`.
    """
    if agent_id is None or environment_id is None:
        cfg = provision()
        agent_id = agent_id or cfg["agent_id"]
        environment_id = environment_id or cfg["environment_id"]

    session_id = start_session(agent_id, environment_id, title=title)
    text = ""
    tool_calls: list[str] = []
    for ev in send_and_stream(session_id, question):
        if ev.type == "agent.message":
            text += _text(ev.content)
        elif ev.type == "agent.tool_use":
            tool_calls.append(ev.name)

    _attach_run_metadata(
        session_id=session_id,
        agent_id=agent_id,
        model=MODEL,
        tool_calls=tool_calls,
    )

    if cleanup:
        try:
            delete_session(session_id)
        except Exception:  # pragma: no cover
            pass

    return {"output": text.strip(), "tool_calls": tool_calls, "session_id": session_id}


if __name__ == "__main__":
    print(json.dumps(provision(), indent=2))
