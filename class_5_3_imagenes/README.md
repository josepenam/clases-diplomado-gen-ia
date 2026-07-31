# Módulo 5 · Clase 3 — Entendimiento y generación de imágenes

Diplomado de Extensión en IA Generativa para Organizaciones.

Esta clase recorre la visión por computador de punta a punta: la visión **"clásica"**
(convoluciones, CNNs y **YOLO** corriendo en vivo sobre tu webcam), el salto a los **LLMs
multimodales** que describen y razonan sobre imágenes, la **generación** de imágenes desde
texto (el arco VAEs → GANs → difusión, aterrizado en `gpt-image-2`), y un caso de negocio
que junta todo: **OCR semántico** — convertir un formulario escaneado y manuscrito en JSON
estructurado. El hilo conductor: la imagen dejó de ser un tipo de dato especial; hoy entra
y sale de los mismos modelos que ya usas para texto.

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
7. Elegir dónde vive cada credencial y **nunca** versionar un `.env` real.

## Prerrequisitos

- Un entorno local con **Python 3.12**.
- **[uv](https://github.com/astral-sh/uv)** para crear y sincronizar los entornos.
- **API key de OpenAI** ([platform.openai.com](https://platform.openai.com)) — lecciones 2,
  3 y 4. Para la lección 3 (generación) la organización debe estar **verificada**.
- Una **webcam** — solo lección 1 (que es local por diseño; las lecciones 2–4 también
  corren en Google Colab).

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
└── leccion4_ocr_semantico/                LECCIÓN 4 · Caso práctico: OCR semántico
    └── ocr_semantico.ipynb
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

Las lecciones 2–4 también corren en **Google Colab** (la primera celda instala lo
necesario); la lección 1 es local por diseño (necesita la webcam y una ventana en vivo).
Cada lección documenta el registro del kernel de Jupyter (`ipykernel`) para su `.venv`.

## Secrets

**Never commit a real `.env`.** Las lecciones 2, 3 y 4 usan `OPENAI_API_KEY`: copia el
`.env.example` de cada lección a `.env` y complétalo. Los `.env` reales están git-ignorados
(por lección y en la raíz del repo) y **nunca** se versionan. En Colab las llaves se leen
desde `google.colab.userdata` con los mismos nombres.

> La lección 1 **no requiere llaves**: YOLO corre offline con pesos descargados de GitHub.
