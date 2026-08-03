# Clases · Diplomado de Extensión en IA Generativa para Organizaciones

Material de clases —código, notebooks y diapositivas— del diplomado, por **José Manuel Peña**.
Cada clase es autocontenida: su propio `README`, su entorno y sus lecciones paso a paso.

## Clases

| Clase | Tema | Contenido |
|---|---|---|
| **3.5 — Deployment** | Llevar un prototipo de GenAI a producción como API | [carpeta](class_3_5_deployment/README.md) · [diapositivas](class_3_5_deployment/deck/deck_3_5_deployment.pptx) |
| **3.6 — Producción** | Evaluar sistemas de LLMs y versionar prompts y skills | [carpeta](class_3_6_production/README.md) · [diapositivas](class_3_6_production/deck/deck_3_6_production.pptx) |
| **5.1 — Modelos open source** | Correr LLMs abiertos localmente (Ollama), afinarlos (fine-tuning) y servirlos rápido (Groq) | [carpeta](class_5_1_opensource/README.md) · [demos interactivos](class_5_1_opensource/deck/serving_llm_a_escala.html) |
| **5.2 — Imágenes** | Detección local (YOLO), entendimiento multimodal, generación (gpt-image-2), OCR semántico, parsing agéntico y RAG visual | [carpeta](class_5_2_imagenes/README.md) · [diapositivas](class_5_2_imagenes/deck/deck_5_2_imagenes.pptx) |
| **5.3 — Voz** | La señal de audio, transcripción, síntesis dirigible, agentes de voz en cascada y modelos voice-to-voice | [carpeta](class_5_3_voz/README.md) · [diapositivas](class_5_3_voz/deck/deck_5_3_voz.pptx) |

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

## Clase 5.1 — Modelos open source

El mundo de los **LLMs open source** de punta a punta: correrlos **localmente**, **afinarlos**
a un corpus y consumirlos **servidos en la nube a alta velocidad**. Tres lecciones, cada una
autocontenida y ejecutable por separado (entorno `uv` propio).

1. **[Lección 1 · LLMs locales con Ollama](class_5_1_opensource/leccion1_ollama_local/)** — qué es Ollama, instalarlo, `ollama pull llama3.2` y consumirlo desde LangChain (`ChatOllama`): invocación, streaming y velocidad local. Sin API keys.
2. **[Lección 2 · Fine-tuning de un LLM](class_5_1_opensource/leccion2_finetuning_llm/)** — DistilGPT2 + subset de WikiText-2 con `Trainer` (transformers v5): tokenización → collator → entrenamiento (minutos en T4/MPS) → comparación con el modelo original.
3. **[Lección 3 · Inferencia con Groq](class_5_1_opensource/leccion3_inferencia_groq/)** — los `gpt-oss` de OpenAI (open-weights) servidos por hardware LPU: la misma tarea de la lección 1 a cientos de tokens por segundo, midiendo t/s reales.

**Recursos visuales** (en `class_5_1_opensource/deck/`, se abren con doble clic):
[`gradient_descent.html`](class_5_1_opensource/deck/gradient_descent.html) — descenso de gradiente en 3D ·
[`serving_llm_a_escala.html`](class_5_1_opensource/deck/serving_llm_a_escala.html) — instrumento interactivo sobre lo que realmente implica servir un LLM (colas, KV cache, paralelismo y un simulador de carga), con cifras medidas en producción ·
[`Open-Weights-and-American-AI-Leadership.pdf`](class_5_1_opensource/deck/Open-Weights-and-American-AI-Leadership.pdf) — la carta de la coalición open-weights (24-07-2026, 77 firmantes).

Más detalle (objetivos, prerrequisitos, entornos): [`class_5_1_opensource/README.md`](class_5_1_opensource/README.md).

---

## Clase 5.2 — Entendimiento y generación de imágenes

La visión por computador de punta a punta: de la visión **clásica** (convoluciones, YOLO) a
los **LLMs multimodales**, la **generación** de imágenes y el aterrizaje en **documentos**
(OCR semántico, parsing agéntico y RAG visual). Seis lecciones, cada una autocontenida y
ejecutable por separado (entorno `uv` propio).

1. **[Lección 1 · YOLO local](class_5_2_imagenes/leccion1_yolo_local/)** — detección y tracking de objetos en vivo sobre la webcam (ultralytics + ByteTrack), 100% local y sin API keys.
2. **[Lección 2 · Entendimiento de imágenes](class_5_2_imagenes/leccion2_vision_llm/)** — imágenes dentro de un `HumanMessage` de LangChain (URL y base64) contra GPT-5: describir, razonar, responder preguntas.
3. **[Lección 3 · Generación de imágenes](class_5_2_imagenes/leccion3_generacion_imagenes/)** — GPT-5 orquesta `gpt-image-2` vía la Responses API (`bind_tools`); la imagen vuelve en base64 y queda en `outputs/`.
4. **[Lección 4 · OCR semántico](class_5_2_imagenes/leccion4_ocr_semantico/)** — caso práctico: un formulario escaneado y manuscrito sale como JSON estructurado (Pydantic + `with_structured_output`).
5. **[Lección 5 · Parsing agéntico](class_5_2_imagenes/leccion5_parsing_agentico/)** — un informe del Banco Central por tres niveles: `pypdf` (US$0), DIY visual con `gpt-5-mini`, y **LlamaParse v2** tier `fast` vs `agentic`. Cierra con el criterio volumen × complejidad × auditabilidad.
6. **[Lección 6 · RAG visual](class_5_2_imagenes/leccion6_rag_visual/)** — buscar páginas por lo que se **ve**: embeddings multimodales (`gemini-embedding-2`) + similitud coseno en numpy, y GPT-5 responde mirando la página. El patrón ColPali en versión API, sin GPU.

**Diapositivas:** [`deck_5_2_imagenes.pptx`](class_5_2_imagenes/deck/deck_5_2_imagenes.pptx)

Más detalle (objetivos, prerrequisitos, entornos): [`class_5_2_imagenes/README.md`](class_5_2_imagenes/README.md).

---

## Clase 5.3 — Voz

La voz de punta a punta, con un hilo conductor que se mide en cada lección: **cada vez que la
voz pasa por texto se pierde información y se gana latencia.** Cuatro lecciones, cada una
autocontenida y ejecutable por separado (entorno `uv` propio).

1. **[Lección 1 · La señal de audio y su transcripción](class_5_3_voz/leccion1_audio_y_transcripcion/)** — muestreo y Nyquist, waveform y espectrograma, la firma de la voz (formantes), y transcripción con `gpt-transcribe`. Cierra degradando la señal con ruido: el modelo aguanta 0 dB sin errar, y al quebrarse **inventa** en vez de callar.
2. **[Lección 2 · Síntesis de voz](class_5_3_voz/leccion2_sintesis_de_voz/)** — `gpt-4o-mini-tts` y el parámetro `instructions`: la misma frase **dirigida** de cuatro formas. Las 13 voces, ElevenLabs `eleven_v3` con acento y clonación, y latencias medidas (`eleven_flash_v2_5` es ~5× más rápido).
3. **[Lección 3 · Agente de voz en cascada](class_5_3_voz/leccion3_agente_sandwich/)** — el método **sándwich**: STT → agente (`create_agent` de LangChain 1.x + búsqueda web) → TTS, con Gradio y micrófono. Presupuesto de latencia por capa, y por qué el modelo del medio se elige por latencia y no por ranking.
4. **[Lección 4 · Voice-to-voice y tres frameworks](class_5_3_voz/leccion4_frameworks_de_voz/)** — `gpt-realtime-2.1` recibe audio y emite audio: la primera sílaba llega **~5× antes**. El mismo agente implementado sin framework, con **OpenAI Agents SDK**, con **Pipecat** (open source) y con **ElevenLabs Agents**, más la tabla de decisión.

**Diapositivas:** [`deck_5_3_voz.pptx`](class_5_3_voz/deck/deck_5_3_voz.pptx)

Más detalle (objetivos, prerrequisitos, entornos): [`class_5_3_voz/README.md`](class_5_3_voz/README.md).

---

## Cómo usar este repo

- **Secretos.** Cada proyecto trae un `.env.example`: cópialo a `.env` y completa tus llaves
  (OpenAI, Qdrant, Anthropic, Groq según la lección). Los `.env` reales **nunca** se versionan — están en `.gitignore`.
- **Colab-first.** Los notebooks corren directo en Google Colab (la primera celda instala lo necesario).
  Para correrlos localmente, cada lección documenta su entorno (`uv` / `poetry`).
- **Requisitos generales:** Docker, una cuenta de fly.io con `flyctl`, Python > 3.11, y las API keys de cada lección.
