# Clases · Diplomado de Extensión en IA Generativa para Organizaciones

Material de clases —código, notebooks y diapositivas— del diplomado, por **José Manuel Peña**.
Cada clase es autocontenida: su propio `README`, su entorno y sus lecciones paso a paso.

## Clases

| Clase | Tema | Contenido |
|---|---|---|
| **3.5 — Deployment** | Llevar un prototipo de GenAI a producción como API | [carpeta](class_3_5_deployment/README.md) · [diapositivas](class_3_5_deployment/deck/deck_3_5_deployment.pptx) |
| **3.6 — Producción** | Evaluar sistemas de LLMs y versionar prompts y skills | [carpeta](class_3_6_production/README.md) · [diapositivas](class_3_6_production/deck/deck_3_6_production.pptx) |

*(Se irán agregando más clases del diplomado.)*

---

## Clase 3.5 — Deployment

De un modelo dentro de un notebook a un **servicio desplegado**, en cuatro lecciones. Se
containeriza con Docker, se sirve una cadena de LangChain sobre HTTP con FastAPI, se despliega
en la nube (fly.io) con CI, y se cierra con RAG sobre una base de datos vectorial.

1. **[Lección 1 · Docker](class_3_5_deployment/leccion1_docker-hello-world/)** — fundamentos de contenedores: `Dockerfile` → imagen → contenedor (build → run).
2. **[Lección 2 · Servir una cadena como API](class_3_5_deployment/leccion2_serve-chain-api/)** — FastAPI expone la cadena `prompt | llm`; Docker; deploy en **fly.io** vía el CLI, con GitHub Actions. Incluye un notebook cliente (HTTP + streaming).
3. **[Lección 3 · Anthropic Managed Agents](class_3_5_deployment/leccion3_anthropic_managed_agents/)** — un agente **hospedado por Anthropic** (Claude): cerebro / manos / sesión desacoplados. Se implementa un "Analista Económico Chile" (ejecuta código contra mindicador.cl + web search) y se consume a través de *sessions* durables.
4. **[Lección 4 · RAG en producción (tarea)](class_3_5_deployment/leccion4_intro_qdrant/)** — chunking → embeddings (OpenAI) → **Qdrant Cloud** → búsqueda por similitud. Semilla de la tarea final.

**Diapositivas:** [`deck_3_5_deployment.pptx`](class_3_5_deployment/deck/deck_3_5_deployment.pptx) · **brief de la tarea:** [`Tarea_RAG.pptx`](class_3_5_deployment/deck/Tarea_RAG.pptx)

Más detalle (objetivos, prerrequisitos, entornos): [`class_3_5_deployment/README.md`](class_3_5_deployment/README.md).

---

## Clase 3.6 — Producción

Cerrar el salto a producción por el lado de la **calidad**: cómo **evaluar** un sistema de LLMs
de forma sistemática y cómo **versionar** los artefactos que lo gobiernan (prompts y skills). Tres
lecciones, cada una autocontenida y ejecutable por separado (entorno `uv` propio).

1. **[Lección 1 · Evaluación con LangSmith](class_3_6_production/leccion1_evaluacion_langsmith/)** — dataset → evaluadores (LLM-as-judge y de referencia) → métrica compuesta `safety_alignment_score` → comparación `gpt-4o-mini` vs `gpt-5-mini`.
2. **[Lección 2 · Versionamiento de prompts](class_3_6_production/leccion2_versionamiento_prompts/)** — el Prompt Hub de LangSmith: descargar prompts, fijar una versión y comparar salidas al reejecutar la cadena.
3. **[Lección 3 · Versionamiento de skills](class_3_6_production/leccion3_versionamiento_skills/)** — skills, standards y commands versionados con **Packmind** y consumidos por un agente LangChain con *progressive disclosure* (context engineering).

**Diapositivas:** [`deck_3_6_production.pptx`](class_3_6_production/deck/deck_3_6_production.pptx)

Más detalle (objetivos, prerrequisitos, entornos): [`class_3_6_production/README.md`](class_3_6_production/README.md).

---

## Cómo usar este repo

- **Secretos.** Cada proyecto trae un `.env.example`: cópialo a `.env` y completa tus llaves
  (OpenAI, Qdrant, Anthropic según la lección). Los `.env` reales **nunca** se versionan — están en `.gitignore`.
- **Colab-first.** Los notebooks corren directo en Google Colab (la primera celda instala lo necesario).
  Para correrlos localmente, cada lección documenta su entorno (`uv` / `poetry`).
- **Requisitos generales:** Docker, una cuenta de fly.io con `flyctl`, Python > 3.11, y las API keys de cada lección.
