# leccion2_skills_y_gestion

**Agent Skills: conocimiento procedural empaquetado, y cómo se gestiona en equipo.** El `SKILL.md` es un estándar abierto desde diciembre de 2025 ([agentskills.io](https://agentskills.io)) — el mismo archivo lo entienden Claude Code, Codex, Copilot, Cursor y decenas de herramientas. La lección lo desarma por dentro (un skill-loader de ~30 líneas sobre la API cruda de OpenAI), mide el contraste con/sin skill, y muestra la distribución multi-agente con [Packmind](https://packmind.com): la misma skill materializada para Claude Code y Cursor con un `install`.

Segunda lección de la Clase 5.4 — Integraciones. El *versionado* de skills (v1→v2, packages, lockfile) lo cubre la [clase 3.6 L3](../../class_3_6_production/leccion3_versionamiento_skills/); acá el foco es el estándar, el mecanismo y la distribución.

## Qué hace

| Paso | Detalle |
|---|---|
| Anatomía | Tres skills de operaciones del centro de esquí en [`skills/`](skills/): frontmatter (siempre visible) + cuerpo (bajo demanda). Por qué la `description` es la pieza crítica. |
| El mecanismo | Skill-loader de ~30 líneas: catálogo en el system prompt + herramienta `cargar_skill` + loop manual de tool-calling con `gpt-5-mini`. Progressive disclosure = inyección condicional de contexto. |
| El contraste | El parte de nieve con y sin skill: formato oficial y línea de cierre verificados programáticamente. El loader carga **solo** la skill que aplica. |
| La cuenta de tokens | Todo-en-prompt vs progressive disclosure, con honestidad: con 3 skills el loader pierde (paga dos llamadas); la pendiente es lo que gana con ~50. |
| Packmind | `init` (multi-agente) → `playbook add/submit` → `packages create/add` → `install` en un proyecto consumidor → la skill materializada en `.claude/skills/` y `.cursor/skills/`. |
| El fallback | `distribuir_skill()` casero (~20 líneas) que renderiza el SKILL.md para tres agentes — enseña qué hace Packmind por dentro y corre sin cuenta ni Node. |

## Requisitos

- Python 3.12 y [uv](https://github.com/astral-sh/uv), o Google Colab (la primera celda baja las skills del repo).
- `OPENAI_API_KEY` — para el loader y el contraste (~5 llamadas a `gpt-5-mini`; costo despreciable).
- **Opcional** para la sección de Packmind: Node ≥ 20 (la CLI corre con `npx @packmind/cli`) y `PACKMIND_API_KEY_V3` (cuenta gratis en [app.packmind.com](https://app.packmind.com), o la instancia self-hosted de tu organización — Packmind es [open source](https://github.com/PackmindHub/packmind)). Sin esto, el fallback local enseña el mecanismo igual.

## Configuración

```bash
# 1. Copia la plantilla de secretos y completa tus llaves
cp .env.example .env          # edita OPENAI_API_KEY (y PACKMIND_API_KEY_V3 si tienes)

# 2. Sincroniza el entorno (crea .venv con las dependencias fijadas)
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
```

## Ejecución local

```bash
# Registra el kernel de Jupyter para este entorno
uv run python -m ipykernel install --user \
  --name clase-5-4-l2 --display-name "Python (clase 5.4 · L2)"

# Abre el notebook
uv run --with jupyterlab jupyter lab skills_y_gestion_de_skills.ipynb
```

Los directorios de trabajo de Packmind (`skill_repo/`, `proyecto_consumidor/`, `proyecto_consumidor_local/`) se regeneran en cada corrida y están git-ignorados.

## Notas

- El menú de `packmind init` es multi-select por stdin (`1,2,6` = AGENTS.md + Claude Code + Cursor); el notebook lo pasa con `stdin_text` para no colgar el kernel.
- El `install` de Packmind materializa las **skills** en la carpeta nativa de cada agente (`.claude/skills/`, `.cursor/skills/` — mismo SKILL.md, el estándar en acción); los *standards* (reglas siempre activas) son los que viajan al `AGENTS.md`.
- El servidor de Packmind a veces devuelve 500 transitorios: el helper `packmind()` reintenta (las operaciones son idempotentes).

## Referencias

- https://agentskills.io (la especificación)
- https://github.com/anthropics/skills (skills oficiales curadas)
- https://skills.sh (marketplace comunitario)
- https://docs.packmind.com
