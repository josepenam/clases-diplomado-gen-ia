# anthropic-managed-agents

A minimal example of **building an agent on Claude Managed Agents** — Anthropic's hosted
agent platform — instead of serving it yourself.

In lección 2 we owned the whole stack: FastAPI, Docker, fly.io. Here the platform hosts the
three pieces of an agent for us, fully decoupled:

- **The session** — a durable, append-only event log server-side. The only permanent piece;
  it outlives your process, your laptop, and the context window.
- **The brain** — Claude + the agent loop. Stateless, disposable.
- **The hands** — a cloud sandbox where the agent runs code. Provisioned on demand, gone when done.

Because the state lives in the session, any client can attach, resume, or replay a
conversation with three API calls: `environments.create` → `agents.create` → `sessions.create`.

## What it builds

An **"Analista Económico Chile"**: an agent whose sandbox can only reach
[mindicador.cl](https://mindicador.cl/api) (free public API — UF, dólar observado, UTM, IPC,
IMACEC…), so it answers with hard data by *running Python*, and uses the built-in
`web_search`/`web_fetch` tools for broader context (news, causes). Reports it writes to
`/mnt/session/outputs/` are downloadable through the Files API.

| Piece | Where | What |
|---|---|---|
| `agent.py` | this folder | provisioning (`provision()`) + session helpers |
| `agent_config.json` | this folder (git-ignored) | cached agent/environment ids after first provision |
| `Test_managed_agent_sessions.ipynb` | this folder | the lesson: consume the agent through sessions |

## Setup

You need an **`ANTHROPIC_API_KEY` with Managed Agents (beta) access** — create a `.env`
(copy `.env.example`) here or at the class root:

```
ANTHROPIC_API_KEY=<your-api-key>
```

The Python deps (`anthropic`, `python-dotenv`, `ipykernel`) are part of the class uv environment:

```bash
cd class_3_5_deployment
uv sync
```

**Kernel (important).** The notebook must run on *this* env — not the shared `clases` kernel (which
has no `anthropic`). Register it once and pick it in VS Code / Jupyter:

```bash
uv run python -m ipykernel install --user --name clase-3-5 --display-name "Python (clase 3.5)"
```

Then in the notebook's kernel picker choose **"Python (clase 3.5)"** (or select the interpreter
`class_3_5_deployment/.venv/bin/python`). A `ModuleNotFoundError: No module named 'anthropic'`
means the wrong kernel is selected.

## Provision (once)

```bash
uv run python leccion3_anthropic_managed_agents/agent.py
```

Creates the sandbox environment and the agent, and caches their ids in `agent_config.json`
(re-running reuses them). The notebook's first cell also calls `agent.provision()`, so you can skip
this step and just run the notebook. Everything else — creating sessions, streaming events, resuming,
downloading reports — happens in the notebook (run it from **this folder**, so `import agent` resolves):

```bash
uv run --with jupyterlab jupyter lab leccion3_anthropic_managed_agents/Test_managed_agent_sessions.ipynb
```

## Cleanup

Sessions cost tokens while active; the notebook's last cell deletes the demo session
(`delete_session`). The agent and environment definitions are free to keep around.

## References

- Workshop this lesson is based on: [anthropics/cwc-workshops](https://github.com/anthropics/cwc-workshops)
  (`ship-your-first-managed-agent` for the Python patterns, `research-desk` for the full
  multi-agent research desk).
- Slide content for the deck: [`SLIDES.md`](SLIDES.md).
