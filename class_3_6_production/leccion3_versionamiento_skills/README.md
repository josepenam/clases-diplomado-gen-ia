# leccion3_versionamiento_skills

**Versionamiento de skills, standards y commands con Packmind + agente LangChain**: crea los
tres artefactos de un agente de código, súbelos y versiónalos con Packmind, agrúpalos en un
package, despliégalos con un *lockfile* y consúmelos desde un agente LangChain.

Tercera de las tres lecciones de la Clase 3.6. Extiende la Lección 2 (versionar *prompts*) a los
artefactos completos de un agente: **skill** (agent-discovered, bajo demanda), **standard**
(regla siempre activa) y **command** (invocado por el usuario), con el *context engineering* de
cargar en el contexto solo lo relevante, solo cuando hace falta.

## Qué hace

| Paso | Detalle |
|---|---|
| Skill v1 | `init` crea el repo; escribe `.claude/skills/<slug>/SKILL.md` (frontmatter + cuerpo) y la sube: `playbook add` + `submit`. |
| Standard + command | Escribe `.claude/rules/<slug>.md` (regla siempre activa) y `.claude/commands/<slug>.md` (acción del usuario) y los versiona igual. |
| Package | `packages create` + `packages add --skill/--standard/--command` agrupa los tres; Packmind versiona automáticamente. |
| Despliegue | `install` deja los tres en `agent_workdir/.claude/{skills,rules,commands}/…` y escribe `packmind-lock.json` (pinning). |
| Agente | `create_agent` con `load_skill`: el standard va **siempre** en el system prompt, la skill se carga **bajo demanda**, el command dispara la tarea. |
| Skill v2 | Cambia el `SKILL.md`, re-`submit` (nueva versión), re-`install`, y reejecuta el mismo command para comparar. |

## Requisitos
- Python 3.12 y [uv](https://github.com/astral-sh/uv).
- **Node.js ≥ 20** (con `npm`/`npx`): la CLI de Packmind se ejecuta con `npx @packmind/cli`.
- Cuenta **gratuita** de Packmind ([app.packmind.ai](https://app.packmind.ai)) y su API key de CLI
  (Settings → CLI Authentication → `PACKMIND_API_KEY_V3`).
- Credenciales de **OpenAI** y de **LangSmith** (el agente traza en LangSmith).

## Configuración
```bash
cp .env.example .env          # edita OPENAI_API_KEY, LANGSMITH_API_KEY y PACKMIND_API_KEY_V3
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
```
El `.env` real nunca se versiona. En Google Colab las llaves se leen desde `google.colab.userdata`
(mismos nombres) y Node ya viene instalado.

## Ejecución local
```bash
uv run python -m ipykernel install --user \
  --name clase-3-6-l3 --display-name "Python (clase 3.6 · L3)"

uv run --with jupyterlab jupyter lab versionamiento_de_skills.ipynb
```
Ejecuta las celdas en orden. El notebook crea `skill_repo/` (donde se autora y versiona la skill,
con su `.claude/skills/`) y `agent_workdir/` (proyecto consumidor donde se instala el package y se
escribe `packmind-lock.json`); ambos están git-ignorados.

> **`init` es interactivo** (pide elegir los agentes destino con un menú numerado); el notebook le
> envía `2` (Claude Code) por stdin. Si tu plan/versión de la CLI difiere (p. ej. `--no-review`
> requiere revisión, o `install` no deja el archivo), el notebook incluye un respaldo que copia el
> `SKILL.md` a mano: el agente sigue funcionando y solo se pierde la demo del lockfile remoto.

## Referencias
- https://docs.packmind.com/tools/cli
- https://docs.packmind.com/concepts/skills-management
- https://docs.langchain.com/oss/python/langchain/multi-agent/skills
