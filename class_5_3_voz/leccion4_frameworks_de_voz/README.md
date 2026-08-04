# leccion4_frameworks_de_voz

**Del sándwich al voice-to-voice, y tres frameworks para construirlo.**

La lección 3 terminó con tres límites que no eran de implementación sino de arquitectura: se
perdía la prosodia del usuario, interrumpir era plomería difícil, y los turnos eran rígidos.
Los tres tienen la misma causa — el audio se convierte en **texto** antes de que el modelo lo
vea, y el texto no tiene tono.

```
SÁNDWICH (lección 3)
  audio ─▶ STT ─▶ texto ─▶ LLM ─▶ texto ─▶ TTS ─▶ audio      3 modelos, 3 saltos

VOICE-TO-VOICE (esta lección)
  audio ────────────▶ LLM ────────────▶ audio                 1 modelo, 0 saltos
```

Cuarta y última lección de la Clase 5.3. Reemplaza la implementación cruda de la API Realtime
del material original por una **comparación de frameworks**: uno open source (Pipecat) y dos
cerrados (OpenAI Agents SDK y ElevenLabs Agents), más el nivel 0 sin framework como
referencia.

## El mismo agente, cuatro veces

Para que la comparación sea entre *frameworks* y no entre demos distintas, los cuatro
programas resuelven el mismo caso —**Luis**, que atiende el teléfono de una ferretería y
consulta el stock con una herramienta— y los cuatro importan el mismo dominio de
[`tienda.py`](tienda.py). El caso viene del `check_product_stock` del material original.

| Archivo | Framework | Qué representa | Modo de verificación |
|---|---|---|---|
| [`nivel0_websocket_crudo.py`](nivel0_websocket_crudo.py) | ninguno | La API a pelo: protocolo, base64 y bucle de eventos a mano. | `--smoke` |
| [`agente_openai.py`](agente_openai.py) | **OpenAI Agents SDK** | `RealtimeAgent` con los mismos primitivos que tus agentes de texto. | `--smoke` |
| [`agente_pipecat.py`](agente_pipecat.py) | **Pipecat** (Daily, BSD) | El pipeline explícito; implementa **las dos** arquitecturas. | `--check` |
| [`agente_elevenlabs.py`](agente_elevenlabs.py) | **ElevenLabs Agents** | El agente vive en la plataforma, no en tu código. | `--check` |

El notebook [`frameworks_de_voz.ipynb`](frameworks_de_voz.ipynb) es la **guía**: explica el
salto de arquitectura, mide la diferencia, corre los modos de verificación de los cuatro
scripts, desarma la mecánica interna de cada framework y sostiene la tabla de decisión. No
abre el micrófono.

## La comparación estructural

La mitad del notebook (una sección propia, *"Cómo funciona cada uno, por dentro"*) responde
a la pregunta que ninguna tabla de features contesta: **¿contra qué vocabulario programas?**
Los números se cuentan **en vivo** por introspección de los paquetes instalados, así que no
envejecen con la lección:

| Framework | Vocabulario | Qué es |
|---|---|---|
| API Realtime a pelo | **56** eventos (11 envías, 45 recibes) | protocolo de cable |
| OpenAI Agents SDK | **15** eventos | una *reducción* de los 56, con `raw_model_event` como escotilla |
| ElevenLabs Agents | **9** eventos (+4 mensajes) | y solo **2** te obligan a actuar (`ping`, `client_tool_call`) |
| Pipecat | **129** frames (45 System / 32 Data / 43 Control / 9 base) | no es un protocolo: es un **bus interno** |

Y desarrolla, para cada uno:

- **Pipecat** — las tres familias de frames y por qué se planifican distinto (un
  `InterruptionFrame` es `SystemFrame` y por eso se adelanta a 3 s de audio ya encolado); las
  dos direcciones (`DOWNSTREAM`/`UPSTREAM`); el ciclo de vida (`StartFrame` → corriendo →
  `EndFrame`); la regla de que **los procesadores no consumen los frames, los pasan**; el
  turno completo etapa por etapa con los frames que cada una emite; y la interrupción como
  `broadcast_interruption()`, que difunde el frame **arriba y abajo** del bus.
- **La API a pelo** — los 45 eventos del servidor agrupados por familia, el turno completo
  anotado evento por evento, el ida y vuelta de la herramienta en dos mensajes (y por qué
  olvidar el segundo `response.create` deja al agente mudo, sin error), y `server_vad` vs
  `semantic_vad`.
- **Agents SDK** — los 15 eventos con su significado, y sobre todo **lo que no aparece** en
  la lista porque el SDK lo absorbió.
- **ElevenLabs** — los 9 eventos, el orden real de un turno, y `agent_response_correction`.

Cierra con **el mismo problema a cuatro alturas**: de quién es el turno, qué oyó realmente el
usuario al interrumpir, y el ida y vuelta de la herramienta. El caso de la interrupción es el
más ilustrativo — mismo problema físico (el audio en el buffer no es el audio que se oyó) y
cuatro tratos distintos: a pelo lo reconcilias tú con `conversation.item.truncate`, el SDK te
avisa con `audio_interrupted`, Pipecat difunde un frame por el bus, y ElevenLabs simplemente
te manda el texto corregido.

## El hallazgo central

Medido en el notebook, partiendo los dos del mismo punto (una pregunta en texto) hasta el
**primer byte de audio**:

| Arquitectura | Primera sílaba |
|---|---|
| Sándwich (`gpt-4.1-mini` → `gpt-4o-mini-tts`) | ~3,3 s |
| Voice-to-voice (`gpt-realtime-2.1`) | **~0,7 s** |

Unas **5× antes**, y la causa no es que un modelo sea más rápido: en el sándwich hay una
**barrera** —el TTS no puede empezar hasta que el LLM terminó de escribir— y el modelo
voice-to-voice no la tiene. Además la medición es generosa con el sándwich, porque le regala
la transcripción (que en la lección 3 costó ~1,3 s más).

El otro hallazgo, que no se mide con cronómetro: Pipecat implementa las dos arquitecturas con
**la misma lista de procesadores menos dos elementos**. El `--check` lo imprime y se ve
`OpenAISTTService` y `OpenAITTSService` desaparecer.

## Requisitos

- Python 3.12 y [uv](https://github.com/astral-sh/uv). **No corre en Colab**: necesita
  micrófono y parlantes locales.
- **`portaudio`** (para PyAudio): `brew install portaudio` en macOS,
  `apt install portaudio19-dev` en Debian/Ubuntu. Sin esto, `uv sync` falla al compilar PyAudio.
- **API key de OpenAI**: https://platform.openai.com — para tres de los cuatro scripts.
- **API key de ElevenLabs** (opcional): https://elevenlabs.io — solo para
  `agente_elevenlabs.py`. Funciona con el plan gratis.

> El pin `requires-python = ">=3.12,<3.13"` no es cosmético acá: Pipecat depende de `audioop`,
> que se eliminó en Python 3.13.

## Configuración

```bash
# 0. La librería de audio del sistema (una sola vez)
brew install portaudio

# 1. Copia la plantilla de secretos y completa tus llaves
cp .env.example .env          # edita OPENAI_API_KEY (y ELEVENLABS_API_KEY si tienes)

# 2. Sincroniza el entorno (crea .venv con las dependencias fijadas)
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
```

## Verificar sin micrófono

Antes de pelearse con el audio conviene comprobar que llaves, modelos y sesiones funcionan:

```bash
uv run python nivel0_websocket_crudo.py --smoke   # handshake + una pregunta de texto
uv run python agente_openai.py --smoke            # sesión del SDK
uv run python agente_pipecat.py --check --modo cascada
uv run python agente_pipecat.py --check --modo realtime
uv run python agente_elevenlabs.py --check        # crea el agente, lo verifica y lo borra
```

## Conversar de verdad

Desde esta carpeta, y se sale con Ctrl-C:

```bash
uv run python agente_openai.py                    # OpenAI Agents SDK
uv run python agente_pipecat.py                   # Pipecat, voice-to-voice
uv run python agente_pipecat.py --modo cascada    # Pipecat, el sándwich — compara al oído
uv run python agente_elevenlabs.py                # ElevenLabs Agents
uv run python nivel0_websocket_crudo.py           # sin framework
```

Tres cosas que vale probar a propósito, porque son justo lo que el sándwich no podía:
**interrumpirlo** mientras habla, **dudar a mitad de frase** ("quiero… un… taladro", que un
VAD por silencio habría cortado y el semántico espera), y **cambiar el tono sin cambiar las
palabras**.

`agente_elevenlabs.py` crea el agente en la plataforma y lo **borra al salir**. Con
`--conservar` queda para verlo en el dashboard.

## El notebook

```bash
uv run python -m ipykernel install --user \
  --name clase-5-3-l4 --display-name "Python (clase 5.3 · L4)"

uv run --with jupyterlab jupyter lab frameworks_de_voz.ipynb
```

## Trampas documentadas

Tres cosas que cuestan una tarde si nadie las avisa:

- **`nltk` vs. `.venv` dentro del proyecto.** Pipecat importa `nltk`, que trae un hook de
  seguridad que bloquea cualquier módulo cuyo origen esté *dentro del directorio de trabajo*.
  Como `.venv` vive justamente ahí (la convención de `uv`), el import se cae con un mensaje
  desorientador sobre `regex`. Se arregla con `NLTK_DISABLE_IMPORT_SECURITY=1`; los scripts ya
  lo hacen por su cuenta antes de importar pipecat.
- **La forma del `session` de la API Realtime cambió.** El material de 2024 usaba
  `input_audio_format: "pcm16"` y `turn_detection` en la raíz; hoy todo va anidado bajo
  `audio.input` / `audio.output` y el formato es un objeto
  (`{"type": "audio/pcm", "rate": 24000}`). Un ejemplo viejo no corre tal cual.
- **Dos restricciones de ElevenLabs Agents.** Un agente en español **debe** usar
  `eleven_flash_v2_5` o `turbo` (la API rechaza los demás), y hay que usar una voz *premade*
  porque las de biblioteca requieren plan pago.

## Referencias

- https://openai.github.io/openai-agents-python/realtime/quickstart/
- https://docs.pipecat.ai/overview/introduction
- https://elevenlabs.io/docs/eleven-agents/libraries/python
- https://developers.openai.com/api/docs/guides/realtime
- https://developers.openai.com/api/docs/models/gpt-realtime-2.1
