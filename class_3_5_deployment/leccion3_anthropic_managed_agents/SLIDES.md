# Lección 3 — diapositivas (contenido fuente)

Cuatro diapositivas en español para agregar a `deck/Modulo 3 clase 5.pptx`.
Formato: título, bullets, y notas del presentador.

---

## Diapositiva 1 — Claude Managed Agents: separar el cerebro de las manos

**Bullets:**
- Hasta ahora: nosotros servimos el modelo (FastAPI + Docker + fly.io). Ahora: Anthropic hospeda el **agente completo**.
- **Sesión** = log de eventos durable en el servidor → *lo único permanente*.
- **Cerebro** = Claude + loop del agente → sin estado, desechable.
- **Manos** = sandbox en la nube (ejecuta código) → se crea y destruye por demanda.
- Seguridad: las credenciales **nunca entran al sandbox** — un proxy las inyecta al momento de la llamada (Vaults).

**Notas del presentador:**
Contrastar con lección 2: allá el contenedor era una "mascota" (si muere, se pierde la conversación). Acá los tres componentes están desacoplados: si el sandbox muere, la sesión sigue intacta. De ese único cambio arquitectónico salen la resiliencia, el paralelismo y la seguridad. Mencionar que Claude no puede filtrar un token que nunca vio.

---

## Diapositiva 2 — Un agente en 3 llamadas de API

**Bullets:**
- `POST /v1/environments` → el sandbox: networking (abierto o restringido por host), paquetes pip.
- `POST /v1/agents` → nombre, modelo, system prompt, tools.
- `POST /v1/sessions` → une agente + ambiente; parte inactiva hasta el primer evento.
- Los eventos son **bidireccionales**: enviamos `user.message`, recibimos `agent.message`, `agent.tool_use`, `session.status_idle`.

**Notas del presentador:**
Mostrar `agent.py`: `setup_environment()`, `setup_agent()`, `start_session()` son literalmente una llamada cada una. El loop de consumo es: abrir el stream de eventos → enviar mensaje → iterar hasta `idle`. Igual que el patrón SSE de lección 2, pero el "servidor" es la plataforma.

---

## Diapositiva 3 — Demo: un Analista Económico Chileno

**Bullets:**
- System prompt: "Eres el Analista Económico Chile…" — datos duros vía **mindicador.cl** (UF, dólar, UTM, IPC — API pública, sin key).
- El sandbox solo puede alcanzar `mindicador.cl` → el agente **ejecuta Python** para consultar y analizar series.
- `web_search` / `web_fetch` habilitados para el contexto (noticias, causas) — corren fuera del sandbox.
- Los informes se escriben en `/mnt/session/outputs/` y se descargan por la Files API.

**Notas del presentador:**
Correr la demo en vivo desde el notebook: preguntar el valor de la UF (se ve el `tool_use` del sandbox consultando la API), luego pedir el análisis del dólar del último año con contexto de noticias → descargar `informe.md`. Punto clave: no le dimos una tool "get_uf" — le dimos *capacidad de ejecutar código* y la descripción de la API; el agente escribe la integración solo.

---

## Diapositiva 4 — Sesiones: estado que sobrevive

**Bullets:**
- El log de eventos es *append-only*: se puede **listar, reanudar y reproducir** cualquier conversación desde cualquier cliente.
- Sesiones de 10+ horas; la compactación de contexto es automática (el log crudo nunca se muta).
- Demo: reiniciar el kernel del notebook → `list_sessions()` + `load_history()` → seguir la misma conversación.
- Qué sigue: memoria compartida entre sesiones, sub-agentes, outcomes (auto-evaluación con rúbrica), deployments programados (cron).

**Notas del presentador:**
Esta es "la gracia" de la lección: en lección 2 el estado moría con el request; acá vive en el servidor. Cerrar conectando con el research-desk del workshop de Anthropic: la misma primitiva escala a un head-of-research que despacha analistas en paralelo (map-reduce de sesiones) y publica un memo semanal con un deployment cron.
