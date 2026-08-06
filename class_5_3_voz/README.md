# Módulo 5 · Clase 3 — Voz

Diplomado de Extensión en IA Generativa para Organizaciones.

Esta clase recorre la voz de punta a punta y en un solo arco: qué **es** una señal de audio
(muestreo, waveform, espectrograma) y cómo se convierte en texto; el camino inverso, la
**síntesis**, con el cambio que define esta generación de modelos —hoy la actuación se
*dirige* en lenguaje natural—; el armado de un **agente conversacional** encadenando tres
modelos (el método **sándwich**); y el salto a los modelos **voice-to-voice**, que reciben
audio y devuelven audio sin pasar por texto, comparados en tres frameworks distintos.

El hilo conductor es una tensión que se hace explícita y medible: **cada vez que la voz pasa
por texto se pierde información y se gana latencia.** La clase mide esa pérdida en cada
lección en vez de afirmarla.

---

## Objetivos de aprendizaje

Al terminar la clase, un estudiante puede:

1. Explicar qué define una señal de audio (**frecuencia de muestreo**, profundidad de bits,
   canales) y por qué el **teorema de Nyquist** pone un techo que ningún modelo puede levantar.
2. Leer un **espectrograma** y reconocer en él la firma de la voz (fundamental, armónicos,
   formantes), y explicar por qué esa representación permitió al reconocimiento de voz heredar
   los avances de la visión por computador.
3. Transcribir audio con **`gpt-transcribe`** y elegir con criterio dentro de la familia
   (streaming, diarización, traducción).
4. Reconocer **cómo falla** un modelo de transcripción cuando la señal se degrada: aguanta
   mucho más ruido de lo esperable, y al quebrarse **inventa** en vez de callar.
5. Sintetizar voz con **`gpt-4o-mini-tts`** y **dirigir la actuación** con `instructions`,
   entendiendo que es control de estilo y no de duración.
6. Comparar OpenAI y **ElevenLabs** con criterios de catálogo, acento, costo y latencia, y
   sostener la conversación de **consentimiento y fraude** que trae la clonación de voz.
7. Construir un agente de voz por el **método sándwich** (STT → agente → TTS) con LangChain
   1.x, escribiendo un prompt **para voz** y no para chat.
8. Instrumentar el **presupuesto de latencia** por capa, y elegir el modelo del medio por
   latencia en vez de por ranking — asumiendo el intercambio con la calidad de la respuesta.
9. Explicar por qué un modelo **voice-to-voice** elimina la barrera del texto, y medir la
   diferencia en tiempo hasta la primera sílaba.
10. Elegir entre **Pipecat**, **OpenAI Agents SDK** y **ElevenLabs Agents** según dónde
    conviene que viva la lógica, cuánto lock-in se acepta y qué hay que autohospedar.
11. Elegir dónde vive cada credencial y **nunca** versionar un `.env` real.

## Prerrequisitos

- Un entorno local con **Python 3.12**.
- **[uv](https://github.com/astral-sh/uv)** para crear y sincronizar los entornos.
- **API key de OpenAI** ([platform.openai.com](https://platform.openai.com)) — las cuatro
  lecciones.
- **API key de ElevenLabs** ([elevenlabs.io](https://elevenlabs.io)) — opcional, lecciones 2 y
  4. Plan gratis de 10.000 caracteres/mes, sin tarjeta.
- **API key de Tavily** ([tavily.com](https://tavily.com)) — opcional, lección 3. Plan gratis
  de 1.000 búsquedas/mes.
- Un **micrófono** — lecciones 3 (la parte de Gradio) y 4.
- **`portaudio`** — solo lección 4: `brew install portaudio` (macOS) o
  `apt install portaudio19-dev` (Debian/Ubuntu).

> Las lecciones 1 a 3 corren también en **Google Colab**. La **lección 4 es local por
> diseño**: necesita micrófono, parlantes y un bucle de audio en vivo.

> Sin las llaves opcionales los notebooks corren igual: esas celdas se saltan con un aviso
> claro y el resto funciona.

---

## Estructura del proyecto

```
class_5_3_voz/
├── README.md                                  ← este archivo
├── deck/
│   └── deck_5_3_voz.pptx                      Diapositivas de la clase
├── data/                                      Insumos locales (vacío por convención)
├── outputs/                                   Artefactos generados (git-ignorado salvo .gitkeep)
├── leccion1_audio_y_transcripcion/            LECCIÓN 1 · La señal de audio y su transcripción
│   ├── transcripcion_de_voz.ipynb
│   └── data/{muestra_musical.wav, muestra_voz.wav}
├── leccion2_sintesis_de_voz/                  LECCIÓN 2 · Síntesis de voz dirigible
│   └── sintesis_de_voz.ipynb
├── leccion3_agente_sandwich/                  LECCIÓN 3 · Agente de voz en cascada
│   └── agente_de_voz_sandwich.ipynb
└── leccion4_frameworks_de_voz/                LECCIÓN 4 · Voice-to-voice y tres frameworks
    ├── frameworks_de_voz.ipynb                guía + tabla de decisión
    ├── tienda.py                              el dominio compartido por los cuatro scripts
    ├── nivel0_websocket_crudo.py              sin framework
    ├── agente_openai.py                       OpenAI Agents SDK
    ├── agente_pipecat.py                      Pipecat (implementa las dos arquitecturas)
    └── agente_elevenlabs.py                   ElevenLabs Agents
```

Cada lección es **autocontenida**: su propio `README`, su entorno `uv` (`pyproject.toml` +
`uv.lock`), su `.gitignore` y su `.env.example`. Cada una corresponde a un tramo del deck.

### Lección 1 — `leccion1_audio_y_transcripcion/`  *(deck: la señal de audio → speech-to-text)*

Antes de llamar a ningún modelo, mirar el dato: muestreo y Nyquist, **waveform**,
**espectrograma**, y la firma particular de la voz. Después la transcripción con
`gpt-transcribe`. Cierra con el experimento que une las dos mitades: ruido blanco a siete
niveles de SNR, tres repeticiones cada uno, hasta que el modelo se quiebra.

El resultado es el corazón de la lección: aguanta 0 dB sin un error, a −5 dB avisa
(`[inaudible]`), y a −10 dB **inventa** — reemplaza el nombre propio por el que su prior de
lenguaje considera más probable. Falla fluido, que es la peor forma de fallar.

```bash
cd leccion1_audio_y_transcripcion
cp .env.example .env                       # OPENAI_API_KEY
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
uv run --with jupyterlab jupyter lab transcripcion_de_voz.ipynb
```

### Lección 2 — `leccion2_sintesis_de_voz/`  *(deck: text-to-speech + ElevenLabs)*

El camino inverso, con el cambio que importa: `instructions` permite **dirigir la actuación**
en lenguaje natural. La misma frase de atención al cliente, cuatro entregas distintas. Después
las 13 voces, y ElevenLabs `eleven_v3` con su catálogo por acento y la conversación sobre
clonación. Cierra midiendo latencia: **`eleven_flash_v2_5` es ~5× más rápido** que los modelos
expresivos, que es el argumento para elegir por latencia cuando la voz es conversacional.

```bash
cd leccion2_sintesis_de_voz
cp .env.example .env                       # OPENAI_API_KEY (+ ELEVENLABS_API_KEY opcional)
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
uv run --with jupyterlab jupyter lab sintesis_de_voz.ipynb
```

### Lección 3 — `leccion3_agente_sandwich/`  *(deck: agentes conversacionales)*

Las dos lecciones anteriores alrededor de un agente: **STT → agente → TTS**. El agente con
`create_agent` de LangChain 1.x y búsqueda web, con un prompt escrito **para voz** (sin listas,
sin markdown, cifras como se pronuncian). Interfaz Gradio con micrófono.

Dos hallazgos medidos: el modelo del medio se elige por **latencia** (un modelo con
razonamiento se toma decenas de segundos, aunque suela dar la mejor respuesta — el intercambio
se nombra explícitamente), y la capa que más pesa es el **TTS**, no el agente.

```bash
cd leccion3_agente_sandwich
cp .env.example .env                       # OPENAI_API_KEY (+ TAVILY_API_KEY opcional)
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
uv run --with jupyterlab jupyter lab agente_de_voz_sandwich.ipynb
```

### Lección 4 — `leccion4_frameworks_de_voz/`  *(deck: la API Realtime y el estado del arte)*

El salto de arquitectura: `gpt-realtime-2.1` recibe audio y **emite audio**. Se elimina la
barrera de esperar el texto completo y se deja de tirar a la basura el tono del usuario.
Medido: la primera sílaba llega **~5× antes** (~0,7 s vs ~3,3 s).

El mismo agente —Luis, de una ferretería, con una herramienta de stock— implementado cuatro
veces: sin framework, con el **OpenAI Agents SDK**, con **Pipecat** (que implementa las dos
arquitecturas con la misma lista menos dos elementos) y con **ElevenLabs Agents**. Cierra con
la tabla de decisión.

```bash
cd leccion4_frameworks_de_voz
brew install portaudio                     # una sola vez, para PyAudio
cp .env.example .env                       # OPENAI_API_KEY (+ ELEVENLABS_API_KEY opcional)
UV_CACHE_DIR=.uv-cache uv sync --python 3.12

uv run python agente_pipecat.py            # conversar (Ctrl-C para salir)
uv run python agente_pipecat.py --check    # o solo verificar, sin micrófono
```

---

## Entornos

Cada lección tiene su **propio** entorno `uv` aislado, para que puedas correr cualquiera por
separado sin resolver dependencias de las demás.

| Lección | Manager / Python | Dependencias clave |
|---|---|---|
| `leccion1_audio_y_transcripcion/` | **uv** · `>=3.12,<3.13` | openai 2.52.0 · numpy 2.5.1 · scipy 1.18.0 · matplotlib 3.11.1 |
| `leccion2_sintesis_de_voz/` | **uv** · `>=3.12,<3.13` | openai 2.52.0 · elevenlabs 2.60.0 |
| `leccion3_agente_sandwich/` | **uv** · `>=3.12,<3.13` | langchain 1.3.14 · langchain-openai 1.4.1 · langchain-tavily 0.2.18 · gradio 6.22.0 |
| `leccion4_frameworks_de_voz/` | **uv** · `>=3.12,<3.13` | openai-agents 0.19.2 · pipecat-ai 1.7.0 · elevenlabs 2.60.0 |

Las lecciones 1 a 3 también corren en **Google Colab** (la primera celda instala lo necesario);
la lección 4 es local por diseño. Cada lección documenta el registro del kernel de Jupyter
(`ipykernel`) para su `.venv`: `clase-5-3-l1` … `clase-5-3-l4`.

> El pin `>=3.12,<3.13` no es cosmético en la lección 4: Pipecat depende de `audioop`, que se
> eliminó en Python 3.13.

## Secrets

**Never commit a real `.env`.** Las cuatro lecciones usan `OPENAI_API_KEY`; la 2 y la 4 suman
`ELEVENLABS_API_KEY` y la 3 `TAVILY_API_KEY` (todas opcionales: sin ellas esas celdas se
saltan). Copia el `.env.example` de cada lección a `.env` y complétalo. Los `.env` reales están
git-ignorados (por lección y en la raíz del repo) y **nunca** se versionan. En Colab las llaves
se leen desde `google.colab.userdata` con los mismos nombres.

> El material antiguo del curso usaba `ELEVEN_API_KEY`; el SDK actual espera
> `ELEVENLABS_API_KEY`. Los notebooks y scripts aceptan las dos.

## Nota sobre modelos

El material fuente de esta clase es de enero de 2026 y los modelos de voz se movieron mucho
desde entonces. Lo que se actualizó al portarla:

| El material usaba | Ahora usa | Por qué |
|---|---|---|
| `whisper-1`, `gpt-4o-transcribe` | **`gpt-transcribe`** | Es el modelo recomendado para transcripción de archivo. |
| `tts-1` + `stream_to_file()` | **`gpt-4o-mini-tts`** + `with_streaming_response` | `tts-1`/`tts-1-hd` son legacy; `stream_to_file` está deprecado. |
| 6 voces | **13 voces** (`marin` y `cedar` recomendadas) | — |
| — | el parámetro **`instructions`** | Se puede dirigir la actuación; no existía antes. |
| `eleven_multilingual_v2` | **`eleven_v3`** / `eleven_flash_v2_5` | Modelos actuales; el `flash` para tiempo real. |
| `create_tool_calling_agent` + `AgentExecutor` | **`create_agent`** (LangChain 1.x) | Ambos deprecados. |
| `langchain_community.tools.tavily_search` | **`langchain-tavily`** | Deprecado. |
| `gpt-4o-realtime-preview-2024-12-17` | **`gpt-realtime-2.1`** | La forma del `session` config cambió por completo. |
| `ipywebrtc` | **Gradio** | `ipywebrtc` ya no funciona en los Jupyter/Colab actuales. |

Quedan mencionados como frontera, sin implementar: `gpt-4o-transcribe-diarize` (saber **quién**
habló), `gpt-realtime-whisper` (transcripción en streaming sub-segundo) y
`gpt-realtime-translate` (traducción simultánea, 70+ idiomas de entrada a 13 de salida).
