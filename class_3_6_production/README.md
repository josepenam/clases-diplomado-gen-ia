# Módulo 3 · Clase 6 — Evaluación y producción de LLMs

Diplomado de Extensión en IA Generativa para Organizaciones.

Esta clase cierra el salto a producción por el lado de la **calidad**: cómo **evaluar** un
sistema de LLMs de forma sistemática y cómo **versionar** los artefactos que lo gobiernan. Se
evalúa con **LangSmith**, se gestiona el ciclo de vida de los **prompts** con el Prompt Hub de
LangSmith y el de las **skills** de agentes con Packmind, consumiéndolas desde un agente
LangChain con *context engineering*.

---

## Objetivos de aprendizaje

Al terminar la clase, un estudiante puede:

1. Explicar por qué un prototipo que "responde bien" no basta: la evaluación es lo que hace
   mantenible y confiable un sistema de LLMs en producción.
2. Construir un **dataset de evaluación** y subirlo a LangSmith (evitando duplicados).
3. Definir **evaluadores** LLM-as-judge y de referencia, y combinarlos en una **métrica
   compuesta** ponderada (`safety_alignment_score`).
4. **Comparar modelos** (`gpt-4o-mini` vs `gpt-5-mini`) sobre el mismo dataset con experimentos.
5. Tratar los **prompts como artefactos versionados** con el Prompt Hub: descargarlos, fijar
   una versión y reejecutarlos en una cadena.
6. Versionar los artefactos de un agente (**skills**, **standards** y **commands**) con Packmind,
   agruparlos en un package y consumirlos desde un agente LangChain (standard siempre activo,
   skill con *progressive disclosure*), fijando la versión desplegada con `packmind-lock.json`.
7. Elegir dónde vive cada credencial y **nunca** versionar un `.env` real.

## Prerrequisitos

- Un entorno local con **Python 3.12**.
- **[uv](https://github.com/astral-sh/uv)** para crear y sincronizar los entornos.
- Una cuenta de **LangSmith** con acceso a la API (las tres lecciones).
- Credenciales de **OpenAI** (las tres lecciones).
- **Node.js ≥ 20** y una cuenta gratuita de **Packmind** (solo lección 3, para la CLI `@packmind/cli`).
- Alternativa sin instalar nada: **Google Colab** (cada notebook trae su celda de instalación).

---

## Estructura del proyecto

```
class_3_6_production/
├── README.md                              ← este archivo
├── deck/
│   └── deck_3_6_production.pptx            Diapositivas de la clase
├── data/                                  Insumos locales (vacío por convención)
├── outputs/                               Artefactos generados (git-ignorado salvo .gitkeep)
├── leccion1_evaluacion_langsmith/         LECCIÓN 1 · Evaluación con LangSmith
│   ├── evaluacion_de_agentes.ipynb
│   └── ejemplos_eval.csv                       dataset de ejemplos (problemas de matemática)
├── leccion2_versionamiento_prompts/       LECCIÓN 2 · Versionamiento de prompts (Prompt Hub)
│   ├── versionamiento_de_prompts.ipynb
│   └── ai_news.txt                             texto de entrada para la cadena
└── leccion3_versionamiento_skills/        LECCIÓN 3 · Versionamiento de skills (Packmind)
    └── versionamiento_de_skills.ipynb          versiona skill/standard/command y los consume un agente LangChain
```

Cada lección es **autocontenida**: su propio `README`, su entorno `uv` (`pyproject.toml` +
`uv.lock`), su `.env.example` y su `.gitignore`. Cada una corresponde a un tramo del deck.

### Lección 1 — `leccion1_evaluacion_langsmith/`  *(deck: "Evaluación con LangSmith")*
Evaluación **dentro de LangSmith**: sube un dataset, define evaluadores (LLM-as-judge y de
referencia), los combina en la métrica compuesta `safety_alignment_score` y compara dos modelos.

```bash
cd leccion1_evaluacion_langsmith
cp .env.example .env                       # OPENAI_API_KEY + LANGSMITH_API_KEY
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
uv run --with jupyterlab jupyter lab evaluacion_de_agentes.ipynb
```

### Lección 2 — `leccion2_versionamiento_prompts/`  *(deck: "Versionamiento de prompts")*
Los prompts como artefactos versionados con el **Prompt Hub** de LangSmith: descarga un prompt
público, uno propio y una **versión fijada**, y compara las salidas al reejecutar la cadena.

```bash
cd leccion2_versionamiento_prompts
cp .env.example .env                       # OPENAI_API_KEY + LANGSMITH_API_KEY
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
uv run --with jupyterlab jupyter lab versionamiento_de_prompts.ipynb
```

### Lección 3 — `leccion3_versionamiento_skills/`  *(deck: "Versionamiento de skills")*
Los tres artefactos de un agente de código versionados con **Packmind**: **skill**
(agent-discovered), **standard** (regla siempre activa) y **command** (invocado por el usuario).
Créalos, súbelos y versiónalos, agrúpalos en un package, despliégalos con un `packmind-lock.json`
y consúmelos desde un **agente LangChain** (standard siempre en contexto, skill bajo demanda con
*progressive disclosure*). Requiere **Node.js** y una cuenta gratuita de Packmind.

```bash
cd leccion3_versionamiento_skills
cp .env.example .env                       # OPENAI_API_KEY + LANGSMITH_API_KEY + PACKMIND_API_KEY_V3
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
uv run --with jupyterlab jupyter lab versionamiento_de_skills.ipynb
```

---

## Entornos

Cada lección tiene su **propio** entorno `uv` aislado, para que puedas correr cualquiera por
separado sin resolver dependencias de las demás.

| Lección | Manager / Python | Dependencias clave |
|---|---|---|
| `leccion1_evaluacion_langsmith/` | **uv** · `>=3.12,<3.13` | langchain 1.3.13 · langchain-core 1.4.9 · langchain-openai 1.3.5 · langsmith 0.9.5 · pandas |
| `leccion2_versionamiento_prompts/` | **uv** · `>=3.12,<3.13` | langchain 1.3.13 · langchain-core 1.4.9 · langchain-openai 1.3.5 · langsmith 0.9.5 |
| `leccion3_versionamiento_skills/` | **uv** · `>=3.12,<3.13` | langchain 1.3.13 · langchain-openai 1.3.5 · langsmith 0.9.5 · pyyaml · CLI `@packmind/cli` (npx) |

Los notebooks también corren en **Google Colab** (la primera celda instala lo necesario), así
que no hace falta reconciliar entornos para seguir la clase. Cada lección documenta el registro
del kernel de Jupyter (`ipykernel`) para su `.venv`.

## Secrets

**Never commit a real `.env`.** Cada lección trae un `.env.example` — cópialo a `.env` y completa
tus llaves. Los `.env` reales están git-ignorados (por lección y en la raíz del repo) y **nunca**
se versionan. En Colab las llaves se leen desde `google.colab.userdata` con los mismos nombres.

> Las plataformas (LangSmith, OpenAI y Packmind) corren en la nube: las llaves viajan a esos
> servicios, no las incrustes en el notebook ni las subas al repo. La API key de Packmind
> (`PACKMIND_API_KEY_V3`) caduca a los 90 días; regénérala en app.packmind.ai cuando expire.
