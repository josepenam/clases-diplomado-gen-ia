# leccion1_audio_y_transcripcion

**La señal de audio y su transcripción.** Antes de llamar a ningún modelo, mirar de qué está
hecha la voz: muestreo, **waveform** y **espectrograma**. Después sí, el camino de la señal al
texto con **`gpt-transcribe`**. Y al final el experimento que une las dos mitades: degradar la
señal con ruido blanco hasta que el modelo se equivoca — y observar **cómo** se equivoca.

Primera lección de la Clase 5.3. Es la contraparte auditiva de lo que la clase 5.2 hacía con
la convolución: entender el dato crudo antes de entregarlo a un modelo.

## Qué hace

| Paso | Detalle |
|---|---|
| Setup | Carga `OPENAI_API_KEY` desde Colab userdata o `.env`. |
| La señal | `data/muestra_musical.wav` — sample rate, bit depth, Nyquist, y qué significa cada uno en la práctica. |
| Waveform | Amplitud en el tiempo con `scipy` + `matplotlib`. |
| Espectrograma | Ventanas + FFT: el audio convertido en **imagen**, que es la razón histórica de que el ASR heredara los avances de la visión por computador. |
| La voz | El mismo análisis sobre `data/muestra_voz.wav`: fundamental, armónicos y formantes, con casi toda la energía útil bajo 4 kHz. |
| Transcripción | `gpt-transcribe`, y cuándo corresponde cada modelo de la familia (streaming, diarización, traducción). |
| Experimento de ruido | Ruido blanco a 7 niveles de SNR (+20 a −15 dB), **tres repeticiones por nivel** sobre audio idéntico. |

El resultado del experimento es el corazón de la lección: el modelo aguanta hasta 0 dB sin
un error, a −5 dB avisa que no le da (`[inaudible]`), y a −10 dB **inventa** — reemplaza el
nombre propio por el que su prior de lenguaje considera más probable. Falla fluido, que es la
peor forma de fallar.

## Requisitos

- Python 3.12 y [uv](https://github.com/astral-sh/uv), o Google Colab.
- API key de OpenAI: https://platform.openai.com — solo para las celdas de transcripción.
  **Sin ella el notebook corre igual**: todo el análisis de la señal es local, y las celdas
  que llaman a la API se saltan con un aviso claro.

El costo de las llamadas es despreciable: 22 transcripciones de ~3 segundos.

## Configuración

```bash
# 1. Copia la plantilla de secretos y completa tu llave
cp .env.example .env          # edita OPENAI_API_KEY

# 2. Sincroniza el entorno (crea .venv con las dependencias fijadas)
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
```

## Ejecución local

```bash
# Registra el kernel de Jupyter para este entorno
uv run python -m ipykernel install --user \
  --name clase-5-3-l1 --display-name "Python (clase 5.3 · L1)"

# Abre el notebook
uv run --with jupyterlab jupyter lab transcripcion_de_voz.ipynb
```

Los audios con ruido que genera el experimento quedan en `outputs/` (git-ignorado).

## Nota sobre los insumos

`data/muestra_musical.wav` y `data/muestra_voz.wav` son **PCM16 real**. El material original
de la clase traía el fragmento musical como `Chorus.wav`, que en realidad era un MP3 con la
extensión equivocada — `scipy.io.wavfile.read()` no puede leerlo. Acá viene transcodificado.

La muestra de voz es sintética (generada con TTS), y el notebook lo dice explícitamente: es
*modo fácil*, sin ruido ni acento ni solapamiento. La dificultad la aporta el experimento de
ruido.

## Referencias

- https://developers.openai.com/api/docs/guides/transcription
- https://arxiv.org/abs/2212.04356 (Whisper — *Robust Speech Recognition via Large-Scale Weak Supervision*)
- https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.spectrogram.html
