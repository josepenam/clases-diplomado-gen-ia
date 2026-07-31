# Módulo 5 · Clase 3 — Entendimiento y generación de imágenes

Diplomado de Extensión en IA Generativa para Organizaciones.

Esta clase recorre la visión por computador de punta a punta: la visión **"clásica"**
(convoluciones, CNNs y **YOLO** corriendo en vivo sobre tu webcam), el salto a los **LLMs
multimodales** que describen y razonan sobre imágenes, la **generación** de imágenes desde
texto (el arco VAEs → GANs → difusión, aterrizado en `gpt-image-2`), y el aterrizaje en
documentos: **OCR semántico** (un formulario manuscrito → JSON), **parsing agéntico** (un
informe con tablas, a escala) y **RAG visual** (buscar páginas por lo que se ve, sin OCR).
El hilo conductor: la imagen dejó de ser un tipo de dato especial; hoy entra y sale de los
mismos modelos que ya usas para texto.

---

## Objetivos de aprendizaje

Al terminar la clase, un estudiante puede:

1. Explicar qué es una **convolución** y cómo una CNN llega de píxeles a clases, y qué hace
   distinto **YOLO** (detección en una sola pasada, en tiempo real).
2. Correr detección y tracking de objetos **local** con ultralytics (webcam, IDs
   persistentes) y reconocer los límites de un detector de clases fijas.
3. Pasarle imágenes a un **LLM multimodal** (GPT-5) vía LangChain — por URL o base64 — y
   conversar sobre su contenido.
4. Describir cómo funcionan **VAEs, GANs y modelos de difusión** (espacio latente, redes
   adversarias, denoising) y ubicar a Stable Diffusion / gpt-image-2 en esa historia.
5. Generar imágenes desde texto con la herramienta `image_generation` de OpenAI orquestada
   por un LLM, entendiendo costos y el requisito de organización verificada.
6. Implementar **OCR semántico**: extraer datos estructurados (esquema Pydantic +
   `with_structured_output`) desde un documento escaneado con manuscrito.
7. Comparar tres niveles de **extracción de documentos** (texto embebido, DIY visual,
   parsing agéntico) y elegir cuál corresponde según volumen × complejidad × auditabilidad.
8. Montar un **RAG visual**: indexar páginas como imágenes con embeddings multimodales y
   recuperar la página correcta por similitud, sin OCR ni chunking.
9. Elegir dónde vive cada credencial y **nunca** versionar un `.env` real.

## Prerrequisitos

- Un entorno local con **Python 3.12**.
- **[uv](https://github.com/astral-sh/uv)** para crear y sincronizar los entornos.
- **API key de OpenAI** ([platform.openai.com](https://platform.openai.com)) — lecciones 2
  a 6. Para la lección 3 (generación) la organización debe estar **verificada**.
- **API key de LlamaCloud** ([cloud.llamaindex.ai](https://cloud.llamaindex.ai)) — solo el
  nivel 2 de la lección 5. Plan Free: 10.000 créditos/mes, sin tarjeta.
- **API key de Gemini** ([aistudio.google.com](https://aistudio.google.com)) — solo la
  lección 6. Gratis.
- Una **webcam** — solo lección 1 (que es local por diseño; las lecciones 2–6 también
  corren en Google Colab).

> Las lecciones 5 y 6 corren **sin** las llaves de LlamaCloud/Gemini: esas celdas se saltan
> con una instrucción clara, y el resto del notebook funciona igual.

---

## Estructura del proyecto

```
class_5_3_imagenes/
├── README.md                              ← este archivo
├── deck/
│   └── deck_5_3_imagenes.pptx             Diapositivas de la clase
├── data/                                  Insumos locales (vacío por convención)
├── outputs/                               Artefactos generados (git-ignorado salvo .gitkeep)
├── leccion1_yolo_local/                   LECCIÓN 1 · Detección y tracking con YOLO
│   └── yolo_tracking.py
├── leccion2_vision_llm/                   LECCIÓN 2 · Entendimiento de imágenes con LLMs
│   └── entendimiento_de_imagenes.ipynb
├── leccion3_generacion_imagenes/          LECCIÓN 3 · Generación con gpt-image-2
│   └── generacion_de_imagenes.ipynb
├── leccion4_ocr_semantico/                LECCIÓN 4 · Caso práctico: OCR semántico
│   └── ocr_semantico.ipynb
├── leccion5_parsing_agentico/             LECCIÓN 5 · Parsing agéntico de documentos
│   ├── parsing_agentico.ipynb
│   └── data/documento_ejemplo.pdf         IPoM jun-2026 cap. II (Banco Central de Chile)
└── leccion6_rag_visual/                   LECCIÓN 6 · RAG visual (sin OCR)
    ├── rag_visual.ipynb
    └── data/documento_ejemplo.pdf         el mismo PDF de la lección 5
```

Cada lección es **autocontenida**: su propio `README`, su entorno `uv` (`pyproject.toml` +
`uv.lock`), su `.gitignore` y — donde usa llaves — su `.env.example`. Cada una corresponde a
un tramo del deck.

### Lección 1 — `leccion1_yolo_local/`  *(deck: "Reconocimiento de imágenes" — convolución → YOLO)*

Detección y tracking de objetos **en tu máquina**: YOLO (ultralytics) sobre la webcam, con
IDs de track persistentes (ByteTrack). Sin API keys. El peso se descarga automático la
primera vez.

```bash
cd leccion1_yolo_local
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
uv run python yolo_tracking.py             # webcam en vivo; cierra con q / Ctrl-C
```

### Lección 2 — `leccion2_vision_llm/`  *(deck: "SOTA: multimodalidad" + ejemplo de análisis)*

El salto de un detector de 80 clases a un modelo que **conversa** sobre la imagen: bloques
de imagen (URL y base64) dentro de un `HumanMessage` de LangChain, contra GPT-5.

```bash
cd leccion2_vision_llm
cp .env.example .env                       # OPENAI_API_KEY
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
uv run --with jupyterlab jupyter lab entendimiento_de_imagenes.ipynb
```

### Lección 3 — `leccion3_generacion_imagenes/`  *(deck: "Generación de imágenes" — VAEs → GANs → difusión)*

La teoría del deck aterrizada en su producto comercial: GPT-5 orquesta `gpt-image-2` vía la
Responses API (`bind_tools`), la imagen vuelve en base64 y queda en `outputs/`.

> Requiere organización de OpenAI **verificada**, y cada imagen cuesta (~US$0.21 en calidad
> alta 1024×1024; ~US$0.006 en baja). Para iterar, baja `quality`.

```bash
cd leccion3_generacion_imagenes
cp .env.example .env                       # OPENAI_API_KEY
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
uv run --with jupyterlab jupyter lab generacion_de_imagenes.ipynb
```

### Lección 4 — `leccion4_ocr_semantico/`  *(deck: "Caso práctico: OCR semántico")*

Un formulario de inspección vehicular — manuscrito, con opciones marcadas a mano — entra
como imagen y sale como **JSON con esquema garantizado** (Pydantic +
`with_structured_output`, gpt-5-mini). El caso de negocio de la clase.

```bash
cd leccion4_ocr_semantico
cp .env.example .env                       # OPENAI_API_KEY
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
uv run --with jupyterlab jupyter lab ocr_semantico.ipynb
```

### Lección 5 — `leccion5_parsing_agentico/`  *(deck: "Documentos a escala")*

El mismo informe del Banco Central por **tres niveles**: `pypdf` (texto embebido, US$0),
DIY visual (`gpt-5-mini` transcribe la página a Markdown) y **LlamaParse v2** en tier `fast`
vs `agentic`, lado a lado. Cierra con el mercado y el criterio de decisión.

```bash
cd leccion5_parsing_agentico
cp .env.example .env                       # OPENAI_API_KEY (+ LLAMA_CLOUD_API_KEY opcional)
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
uv run --with jupyterlab jupyter lab parsing_agentico.ipynb
```

### Lección 6 — `leccion6_rag_visual/`  *(deck: "Buscar por lo que se VE")*

La alternativa al parsing: cada página se indexa **como imagen** con `gemini-embedding-2`,
la pregunta encuentra la página por similitud coseno (numpy, sin base vectorial) y **gpt-5**
responde mirando la página, con cita. Es el patrón ColPali en versión API, sin GPU.

```bash
cd leccion6_rag_visual
cp .env.example .env                       # OPENAI_API_KEY (+ GEMINI_API_KEY opcional)
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
uv run --with jupyterlab jupyter lab rag_visual.ipynb
```

---

## Entornos

Cada lección tiene su **propio** entorno `uv` aislado, para que puedas correr cualquiera por
separado sin resolver dependencias de las demás.

| Lección | Manager / Python | Dependencias clave |
|---|---|---|
| `leccion1_yolo_local/` | **uv** · `>=3.12,<3.13` | ultralytics 8.4.113 (torch 2.13.0 · opencv 5.0.0) |
| `leccion2_vision_llm/` | **uv** · `>=3.12,<3.13` | langchain-openai 1.3.5 · langchain-core 1.4.9 · pillow 12.3.0 |
| `leccion3_generacion_imagenes/` | **uv** · `>=3.12,<3.13` | langchain-openai 1.3.5 · langchain-core 1.4.9 · pillow 12.3.0 |
| `leccion4_ocr_semantico/` | **uv** · `>=3.12,<3.13` | langchain-openai 1.3.5 · langchain-core 1.4.9 · pydantic 2.13.4 |
| `leccion5_parsing_agentico/` | **uv** · `>=3.12,<3.13` | llama-cloud 2.13.0 · pypdf 6.14.2 · pypdfium2 5.12.1 · langchain-openai 1.3.5 |
| `leccion6_rag_visual/` | **uv** · `>=3.12,<3.13` | google-genai 2.16.0 · pypdfium2 5.12.1 · numpy 2.5.1 · langchain-openai 1.3.5 |

Las lecciones 2–6 también corren en **Google Colab** (la primera celda instala lo
necesario); la lección 1 es local por diseño (necesita la webcam y una ventana en vivo).
Cada lección documenta el registro del kernel de Jupyter (`ipykernel`) para su `.venv`.

## Secrets

**Never commit a real `.env`.** Las lecciones 2 a 6 usan `OPENAI_API_KEY`; la lección 5 suma
`LLAMA_CLOUD_API_KEY` y la 6 `GEMINI_API_KEY` (ambas opcionales: sin ellas esas celdas se
saltan). Copia el `.env.example` de cada lección a `.env` y complétalo. Los `.env` reales
están git-ignorados (por lección y en la raíz del repo) y **nunca** se versionan. En Colab
las llaves se leen desde `google.colab.userdata` con los mismos nombres.

> La lección 1 **no requiere llaves**: YOLO corre offline con pesos descargados de GitHub.
