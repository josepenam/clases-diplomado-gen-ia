"""
Lección 3 — a tiny web UI for the "Analista Económico Chile" managed agent.

We don't touch the Anthropic API here: everything goes through the session
helpers already in `agent.py` (provision → start_session → send_and_stream).
This module only adds a thin, dependency-free web layer on top:

    GET  /        → the single-page chat UI (all CSS/JS inline, no CDN)
    POST /chat    → streams the agent's reply back token-by-token
    POST /reset   → drops the current session to start a fresh conversation

Run it (from anywhere — it puts its own folder on sys.path so `import agent`
resolves) and open http://localhost:8080 :

    uv run python leccion3_anthropic_managed_agents/app.py

Uses only the Python standard library (http.server) so there is nothing to
install beyond the class's existing `anthropic` dependency.
"""
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

# Make `import agent` work regardless of the current working directory.
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import agent  # noqa: E402  (must follow the sys.path tweak above)

HOST, PORT = "127.0.0.1", 8080

# ── One shared managed session, created lazily on the first message ──────────
# A single session keeps the conversation's context (the session *is* the
# state), so follow-up questions build on earlier answers. Guarded by a lock
# because the threaded server can handle requests concurrently.
_state = {"agent_id": None, "env_id": None, "session_id": None}
_lock = threading.Lock()


def _ensure_session() -> str:
    """Return the current session id, creating agent/env/session if needed."""
    with _lock:
        if _state["agent_id"] is None:
            cfg = agent.provision()
            _state["agent_id"] = cfg["agent_id"]
            _state["env_id"] = cfg["environment_id"]
        if _state["session_id"] is None:
            _state["session_id"] = agent.start_session(
                _state["agent_id"], _state["env_id"], title="Consulta web"
            )
        return _state["session_id"]


def _reset_session() -> None:
    """Forget the current session so the next message starts a fresh one."""
    with _lock:
        old = _state["session_id"]
        _state["session_id"] = None
    if old:
        try:
            agent.delete_session(old)
        except Exception:
            pass  # best-effort cleanup; a stale session just costs nothing idle


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *_args):  # keep the console clean
        pass

    # ── GET / → the page ─────────────────────────────────────────────────
    def do_GET(self):
        if self.path not in ("/", "/index.html"):
            self.send_error(404)
            return
        body = PAGE.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # ── POST /chat, POST /reset ──────────────────────────────────────────
    def do_POST(self):
        if self.path == "/reset":
            _reset_session()
            self._json({"ok": True})
            return
        if self.path != "/chat":
            self.send_error(404)
            return

        text = (self._read_json().get("message") or "").strip()
        if not text:
            self._json({"error": "Mensaje vacío"}, status=400)
            return

        # Stream the reply. We don't send Content-Length; instead we close the
        # connection when the turn ends, which lets the browser's fetch reader
        # consume chunks as they arrive without any SSE framing.
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "close")
        self.end_headers()

        try:
            session_id = _ensure_session()
            for ev in agent.send_and_stream(session_id, text):
                if ev.type == "agent.message":
                    chunk = agent._text(ev.content)
                    if chunk:
                        self.wfile.write(chunk.encode("utf-8"))
                        self.wfile.flush()
        except BrokenPipeError:
            pass  # client navigated away mid-stream
        except Exception as exc:
            try:
                self.wfile.write(f"\n\n⚠️ Error del servidor: {exc}".encode("utf-8"))
                self.wfile.flush()
            except Exception:
                pass

    # ── small helpers ────────────────────────────────────────────────────
    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if not length:
            return {}
        try:
            return json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            return {}

    def _json(self, obj: dict, status: int = 200):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


PAGE = r"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Analista Económico Chile</title>
<style>
  :root {
    --bg: #f4f1ea; --panel: #fffdf8; --ink: #2b2620; --muted: #8a8175;
    --line: #e7e1d5; --accent: #c1502e; --accent-ink: #fff;
    --user-bg: #e9ede8; --agent-bg: #fffdf8;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #1a1815; --panel: #232019; --ink: #ece7dd; --muted: #9a9184;
      --line: #34302a; --accent: #e2764f; --accent-ink: #1a1815;
      --user-bg: #2c2a24; --agent-bg: #232019;
    }
  }
  * { box-sizing: border-box; }
  html, body { height: 100%; }
  body {
    margin: 0; background: var(--bg); color: var(--ink);
    font: 16px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    display: flex; flex-direction: column; align-items: center;
  }
  .app {
    width: 100%; max-width: 760px; height: 100%;
    display: flex; flex-direction: column; padding: 0 16px;
  }
  header {
    padding: 22px 4px 14px; border-bottom: 1px solid var(--line);
    display: flex; align-items: baseline; gap: 10px; flex-wrap: wrap;
  }
  header h1 { margin: 0; font-size: 20px; font-weight: 650; letter-spacing: -.01em; }
  header .sub { color: var(--muted); font-size: 13px; }
  header .reset {
    margin-left: auto; color: var(--muted); font-size: 13px; cursor: pointer;
    background: none; border: none; text-decoration: underline; padding: 4px;
  }
  header .reset:hover { color: var(--accent); }
  #log {
    flex: 1; overflow-y: auto; padding: 20px 2px; display: flex;
    flex-direction: column; gap: 14px;
  }
  .msg { display: flex; }
  .msg.user { justify-content: flex-end; }
  .bubble {
    max-width: 88%; padding: 11px 15px; border-radius: 16px;
    border: 1px solid var(--line); white-space: pre-wrap; word-wrap: break-word;
  }
  .msg.user .bubble { background: var(--user-bg); border-bottom-right-radius: 5px; }
  .msg.agent .bubble { background: var(--agent-bg); border-bottom-left-radius: 5px; }
  .bubble strong { font-weight: 650; }
  .bubble code {
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: .9em;
    background: rgba(128,128,128,.16); padding: 1px 5px; border-radius: 5px;
  }
  .bubble ul { margin: 6px 0; padding-left: 20px; }
  .bubble .cursor { opacity: .45; }
  .empty {
    color: var(--muted); text-align: center; margin: auto 0; padding: 0 20px;
  }
  .empty .big { font-size: 15px; color: var(--ink); margin-bottom: 6px; }
  .chip {
    display: inline-block; margin: 4px; padding: 6px 12px; font-size: 13px;
    border: 1px solid var(--line); border-radius: 999px; background: var(--panel);
    cursor: pointer; color: var(--ink);
  }
  .chip:hover { border-color: var(--accent); color: var(--accent); }
  form {
    display: flex; gap: 8px; padding: 12px 0 20px; border-top: 1px solid var(--line);
  }
  #input {
    flex: 1; resize: none; font: inherit; color: var(--ink);
    background: var(--panel); border: 1px solid var(--line); border-radius: 12px;
    padding: 11px 14px; max-height: 140px;
  }
  #input:focus { outline: none; border-color: var(--accent); }
  #send {
    border: none; background: var(--accent); color: var(--accent-ink);
    font: inherit; font-weight: 600; border-radius: 12px; padding: 0 20px;
    cursor: pointer;
  }
  #send:disabled { opacity: .5; cursor: default; }
</style>
</head>
<body>
<div class="app">
  <header>
    <h1>Analista Económico Chile 🇨🇱</h1>
    <span class="sub">datos duros vía mindicador.cl</span>
    <button class="reset" id="reset">nueva conversación</button>
  </header>

  <div id="log">
    <div class="empty" id="empty">
      <div class="big">Pregúntame sobre la economía chilena.</div>
      <div>Consulto indicadores en vivo y te respondo con cifras.</div>
      <div style="margin-top:14px">
        <span class="chip">¿Cuál es el valor de la UF y el dólar hoy?</span>
        <span class="chip">Resume el último IMACEC y qué lo explica.</span>
        <span class="chip">Compara el IPC de este año con el anterior.</span>
      </div>
    </div>
  </div>

  <form id="form">
    <textarea id="input" rows="1" placeholder="Escribe tu pregunta…" autofocus></textarea>
    <button id="send" type="submit">Enviar</button>
  </form>
</div>

<script>
const log = document.getElementById('log');
const empty = document.getElementById('empty');
const form = document.getElementById('form');
const input = document.getElementById('input');
const send = document.getElementById('send');
let busy = false;

// Minimal, safe markdown: escape first, then a few inline patterns.
function render(text) {
  let h = text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  h = h.replace(/`([^`]+)`/g, '<code>$1</code>');
  h = h.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  // bullet lines "- " or "* " → <ul><li>
  h = h.replace(/(?:^|\n)([*-] .+(?:\n[*-] .+)*)/g, (m, block) => {
    const items = block.trim().split('\n')
      .map(l => '<li>' + l.replace(/^[*-]\s+/, '') + '</li>').join('');
    return '\n<ul>' + items + '</ul>';
  });
  return h;
}

function addBubble(role, text) {
  empty && empty.remove();
  const msg = document.createElement('div');
  msg.className = 'msg ' + role;
  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.innerHTML = role === 'agent' ? render(text) : text
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  msg.appendChild(bubble);
  log.appendChild(msg);
  log.scrollTop = log.scrollHeight;
  return bubble;
}

function autosize() {
  input.style.height = 'auto';
  input.style.height = Math.min(input.scrollHeight, 140) + 'px';
}
input.addEventListener('input', autosize);
input.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); form.requestSubmit(); }
});

document.querySelectorAll('.chip').forEach(c =>
  c.addEventListener('click', () => { input.value = c.textContent; autosize(); form.requestSubmit(); }));

document.getElementById('reset').addEventListener('click', async () => {
  if (busy) return;
  await fetch('/reset', { method: 'POST' });
  log.innerHTML = '';
  location.reload();
});

form.addEventListener('submit', async e => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text || busy) return;
  busy = true; send.disabled = true;
  addBubble('user', text);
  input.value = ''; autosize();

  const bubble = addBubble('agent', '');
  bubble.innerHTML = '<span class="cursor">▋</span>';
  let acc = '';
  try {
    const resp = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text }),
    });
    const reader = resp.body.getReader();
    const dec = new TextDecoder();
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      acc += dec.decode(value, { stream: true });
      bubble.innerHTML = render(acc) + '<span class="cursor">▋</span>';
      log.scrollTop = log.scrollHeight;
    }
    bubble.innerHTML = render(acc) || '<em>(sin respuesta)</em>';
  } catch (err) {
    bubble.innerHTML = render(acc) + '\n\n⚠️ Se perdió la conexión.';
  } finally {
    busy = false; send.disabled = false; input.focus();
    log.scrollTop = log.scrollHeight;
  }
});
</script>
</body>
</html>
"""


def main():
    print("Provisioning managed agent (reusing cached ids if present)…")
    try:
        agent.provision()
    except Exception as exc:
        print(f"\n❌ No se pudo inicializar el agente: {exc}")
        print("   Revisa que .env tenga un ANTHROPIC_API_KEY con acceso a Managed Agents (beta).")
        sys.exit(1)

    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"\n✅ Analista Económico Chile en  http://localhost:{PORT}")
    print("   (Ctrl+C para detener)\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDeteniendo…")
    finally:
        server.shutdown()
        if _state["session_id"]:
            try:
                agent.delete_session(_state["session_id"])
            except Exception:
                pass


if __name__ == "__main__":
    main()
