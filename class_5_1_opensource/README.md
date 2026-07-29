# Módulo 5 · Clase 1 — Modelos open source

Diplomado de Extensión en IA Generativa para Organizaciones.

Esta clase recorre el mundo de los **LLMs open source** de punta a punta: correr un modelo
abierto **en tu propia máquina** con **Ollama**, **afinarlo** a un corpus con fine-tuning
(Hugging Face `Trainer`), y consumir los mismos modelos abiertos **servidos en la nube a alta
velocidad** con **Groq**. El hilo conductor: con pesos abiertos, tú eliges dónde vive el
modelo — y esa es una decisión de producto, no solo técnica.

El deck cierra el arco de fine-tuning con un bloque sobre **destilación de modelos**: qué es,
su arquitectura general (maestro → señal → estudiante, y la frontera entre destilación de
*caja blanca* y de *caja negra*), las tres formas de hacerla, y la disputa por destilación
entre EE. UU. y China que hoy define el debate open vs closed.

---

## Objetivos de aprendizaje

Al terminar la clase, un estudiante puede:

1. Explicar qué es un modelo **open-weights** y qué opciones hay para ejecutarlo (local,
   nube especializada, fine-tuning propio).
2. Instalar **Ollama**, descargar un modelo (`ollama pull`) y consumirlo desde **LangChain**
   (`ChatOllama`) con invocación, streaming y medición de velocidad local.
3. Hacer **fine-tuning completo** de un LLM pequeño (DistilGPT2) sobre WikiText-2 con la API
   `Trainer`, entendiendo tokenización, data collator y el bucle de entrenamiento.
4. Explicar por qué **los datos definen la lengua y el dominio** del modelo resultante (y qué
   haría falta para un modelo en español).
5. Distinguir **fine-tuning de destilación** (de dónde sale el dato de entrenamiento), describir
   la arquitectura maestro–estudiante y por qué la frontera *caja blanca / caja negra* es la que
   separa una técnica estándar de un conflicto legal.
6. Consumir modelos abiertos servidos por **Groq** (`gpt-oss-20b`/`120b`) y comparar la
   velocidad real (t/s) entre inferencia local y nube especializada.
7. Elegir dónde vive cada credencial y **nunca** versionar un `.env` real.

## Prerrequisitos

- Un entorno local con **Python 3.12**.
- **[uv](https://github.com/astral-sh/uv)** para crear y sincronizar los entornos.
- **Ollama** instalado y el modelo de la lección descargado: `ollama pull llama3.2` (~2 GB) —
  solo lección 1.
- Cuenta **gratuita de Groq** con API key ([console.groq.com](https://console.groq.com)) —
  solo lección 3.
- La lección 2 no requiere llaves; como alternativa sin instalar nada corre en
  **Google Colab** con GPU T4 (la primera celda instala lo necesario). La lección 3 también
  corre en Colab; la lección 1 es **local por diseño**.

---

## Estructura del proyecto

```
class_5_1_opensource/
├── README.md                              ← este archivo
├── deck/
│   ├── gradient_descent.html               Demo interactivo 3D (Three.js) de descenso de
│   │                                       gradiente — ábrelo en el navegador (requiere
│   │                                       internet: carga three.js desde unpkg)
│   ├── serving_llm_a_escala.html           Instrumento interactivo: la máquina real de
│   │                                       servir un LLM (colas, KV cache, paralelismo,
│   │                                       simulador de carga). Autocontenido, offline
│   └── Open-Weights-and-American-AI-       Carta coalición liderada por NVIDIA
│       Leadership.pdf                      (24-07-2026, 77 firmantes) — lectura para
│                                           la discusión open vs closed
├── data/                                  Insumos locales (vacío por convención)
├── outputs/                               Artefactos generados (git-ignorado salvo .gitkeep)
├── leccion1_ollama_local/                 LECCIÓN 1 · LLMs locales con Ollama
│   └── inferencia_local_con_ollama.ipynb
├── leccion2_finetuning_llm/               LECCIÓN 2 · Fine-tuning de un LLM básico
│   └── finetuning_llm.ipynb
└── leccion3_inferencia_groq/              LECCIÓN 3 · Modelos abiertos servidos por Groq
    └── inferencia_con_groq.ipynb
```

Cada lección es **autocontenida**: su propio `README`, su entorno `uv` (`pyproject.toml` +
`uv.lock`), y su `.gitignore` (la lección 3 además trae `.env.example`). Cada una corresponde
a un tramo del deck.

### Lección 1 — `leccion1_ollama_local/`  *(deck: "LLMs en tu máquina")*

Qué es Ollama, cómo instalarlo y cargar un modelo, y cómo consumirlo desde LangChain:
invocación, streaming y velocidad local (t/s). Sin API keys — todo corre en tu computador.

```bash
cd leccion1_ollama_local
ollama pull llama3.2                       # una sola vez (~2 GB); deja Ollama corriendo
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
uv run --with jupyterlab jupyter lab inferencia_local_con_ollama.ipynb
```

### Lección 2 — `leccion2_finetuning_llm/`  *(deck: "Fine-tuning" + demo `gradient_descent.html`)*

Fine-tuning completo de **DistilGPT2** sobre un subset de **WikiText-2** con `Trainer`:
tokenización, data collator, entrenamiento (~250 pasos, minutos en T4/MPS), generación y
comparación contra el modelo original. Los artefactos quedan en `outputs/` (git-ignorado).

> El bloque de **destilación** del deck (slides 21–25) sale directo de esta lección: DistilGPT2
> ya *es* una destilación de GPT-2 (124M → 82M parámetros, 12 → 6 capas). No tiene notebook
> propio; se dicta después del caso práctico y entrega a la discusión open vs closed.

```bash
cd leccion2_finetuning_llm
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
uv run --with jupyterlab jupyter lab finetuning_llm.ipynb
```

### Lección 3 — `leccion3_inferencia_groq/`  *(deck: "Inferencia acelerada en la nube")*

Los modelos **open-weights de OpenAI** (`gpt-oss-20b` y `gpt-oss-120b`) servidos por **Groq**
(hardware LPU): misma traducción que la lección 1, ahora a cientos de tokens por segundo, con
medición de velocidad real vía `token_usage`.

```bash
cd leccion3_inferencia_groq
cp .env.example .env                       # GROQ_API_KEY (LANGSMITH_API_KEY opcional)
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
uv run --with jupyterlab jupyter lab inferencia_con_groq.ipynb
```

---

## Entornos

Cada lección tiene su **propio** entorno `uv` aislado, para que puedas correr cualquiera por
separado sin resolver dependencias de las demás.

| Lección | Manager / Python | Dependencias clave |
|---|---|---|
| `leccion1_ollama_local/` | **uv** · `>=3.12,<3.13` | langchain-ollama 1.1.0 · langchain-core 1.4.9 |
| `leccion2_finetuning_llm/` | **uv** · `>=3.12,<3.13` | transformers 5.13.1 · datasets 4.8.5 · accelerate 1.14.0 · torch 2.12.1 |
| `leccion3_inferencia_groq/` | **uv** · `>=3.12,<3.13` | langchain-groq 1.1.3 · langchain-core 1.4.9 · langsmith 0.9.5 |

Las lecciones 2 y 3 también corren en **Google Colab** (la primera celda instala lo
necesario); la lección 1 es local por diseño (el modelo vive en tu máquina). Cada lección
documenta el registro del kernel de Jupyter (`ipykernel`) para su `.venv`.

## Recursos del deck

Además de las diapositivas, la carpeta `deck/` trae tres piezas de apoyo:

| Recurso | Para qué | Cuándo usarlo |
|---|---|---|
| [`gradient_descent.html`](deck/gradient_descent.html) | Descenso de gradiente en 3D, con superficies y tasa de aprendizaje ajustables. | Al introducir el fine-tuning (lección 2): qué significa «entrenar». |
| [`serving_llm_a_escala.html`](deck/serving_llm_a_escala.html) | Desarma la frase «lo corremos nosotros»: ciclo de vida de una solicitud, simulador de carga (VRAM ↔ concurrencia ↔ latencia), arranque en frío, paralelismo e interconexión, y modos de falla. Cifras de producción medidas (DeepSeek, TraceLab, Mooncake). | Junto al bloque de economía: el break-even supone que un nodo «sirve», y esta página muestra lo que esconde esa palabra. |
| [`Open-Weights-and-American-AI-Leadership.pdf`](deck/Open-Weights-and-American-AI-Leadership.pdf) | La carta del 24-07-2026 impulsada por Jensen Huang, con 77 firmantes — entre ellos Ollama, Hugging Face, LangChain, Unsloth y Nebius, es decir casi todas las herramientas de esta clase. Sin firmar: Anthropic, Amazon, Apple. | Cierre de la discusión open vs closed source. |

Las dos páginas HTML son autocontenidas y se abren con doble clic;
`serving_llm_a_escala.html` funciona **sin conexión** (tipografías del sistema, sin CDN).

## Secrets

**Never commit a real `.env`.** Solo la lección 3 usa llaves: copia su `.env.example` a `.env`
y completa `GROQ_API_KEY` (y opcionalmente `LANGSMITH_API_KEY` para tracing). Los `.env`
reales están git-ignorados (por lección y en la raíz del repo) y **nunca** se versionan. En
Colab las llaves se leen desde `google.colab.userdata` con los mismos nombres.

> Las lecciones 1 y 2 **no requieren llaves**: Ollama corre offline y el fine-tuning usa un
> modelo y dataset públicos de Hugging Face (sin `HF_TOKEN`).
