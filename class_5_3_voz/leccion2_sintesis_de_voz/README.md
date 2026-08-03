# leccion2_sintesis_de_voz

**Texto a voz.** El camino inverso al de la lección 1, con el cambio que define esta
generación de modelos: hoy la síntesis se **dirige**. Al modelo se le pasa el texto *y una
instrucción de actuación en lenguaje natural* — "habla como un ejecutivo tranquilizando a un
cliente", "susurra" — y el mismo texto con la misma voz sale distinto.

Segunda lección de la Clase 5.3. Compara **`gpt-4o-mini-tts`** (OpenAI) con **`eleven_v3`**
(ElevenLabs) y cierra con costo y latencia medidos, porque esa latencia se suma en el
sándwich de la lección 3.

## Qué hace

| Paso | Detalle |
|---|---|
| Setup | Carga `OPENAI_API_KEY` y `ELEVENLABS_API_KEY` desde Colab userdata o `.env`. |
| Historia | Concatenativa → paramétrica → WaveNet/Tacotron → modelos que siguen instrucciones. Por qué recién ahora se puede dirigir la actuación. |
| Lo básico | `gpt-4o-mini-tts` con `with_streaming_response` (el viejo `stream_to_file` está deprecado). |
| `instructions` | La misma frase de atención al cliente en cuatro direcciones: neutra, ejecutivo cálido, locutor enérgico, confidencial. |
| Medición | Duración de cada versión con el módulo `wave` de la stdlib — y por qué ese número **no** es una medición confiable. |
| Catálogo | Las 13 voces de OpenAI (`marin` y `cedar` son las recomendadas). |
| ElevenLabs | Modelos disponibles, catálogo de voces con sus etiquetas de idioma/acento, y síntesis con `eleven_v3`. |
| Clonación | La conversación de consentimiento, fraude por voz clonada y trazabilidad. No se ejecuta. |
| Latencia | Tres proveedores/modelos cronometrados, 3 repeticiones cada uno. |

Dos hallazgos que la lección usa como contenido, no como accidente:

- **`eleven_flash_v2_5` es ~5× más rápido** que los modelos expresivos (~0,5 s vs ~2-2,5 s
  para una frase corta). Es el argumento para elegir por latencia y no por expresividad
  cuando la voz es conversacional.
- **El efecto de `instructions` sobre la duración es real pero inestable** (entre 5% y 30% de
  dispersión según la corrida, sin dirección predecible). Sirve como control de estilo, no de
  timing — y sirve además para enseñar que una sola corrida no es una medición.

## Requisitos

- Python 3.12 y [uv](https://github.com/astral-sh/uv), o Google Colab.
- **API key de OpenAI**: https://platform.openai.com — para toda la primera mitad.
- **API key de ElevenLabs** (opcional): https://elevenlabs.io — plan gratis de 10.000
  caracteres al mes, sin tarjeta. Sin ella esa sección se salta con un aviso claro.

> **Aviso sobre el plan gratis de ElevenLabs:** las voces **premade** funcionan, pero las de
> la **biblioteca de la comunidad** —incluidas las de acento chileno— devuelven
> `402 paid_plan_required`. El notebook maneja ese caso y continúa. Por eso el ejemplo usa una
> voz premade y deja la voz chilena del material original como demostración condicionada al
> plan pago.

El costo en OpenAI es de centavos: ~25 síntesis de frases cortas.

## Configuración

```bash
# 1. Copia la plantilla de secretos y completa tus llaves
cp .env.example .env          # edita OPENAI_API_KEY (y ELEVENLABS_API_KEY si tienes)

# 2. Sincroniza el entorno (crea .venv con las dependencias fijadas)
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
```

## Ejecución local

```bash
# Registra el kernel de Jupyter para este entorno
uv run python -m ipykernel install --user \
  --name clase-5-3-l2 --display-name "Python (clase 5.3 · L2)"

# Abre el notebook
uv run --with jupyterlab jupyter lab sintesis_de_voz.ipynb
```

Todos los audios generados quedan en `outputs/` (git-ignorado).

## Nota sobre nombres de variables de entorno

El material antiguo del curso usaba `ELEVEN_API_KEY`; el SDK actual espera
`ELEVENLABS_API_KEY`. El notebook acepta las dos y hace el fallback, así que un `.env` viejo
sigue funcionando.

## Referencias

- https://developers.openai.com/api/docs/guides/text-to-speech
- https://elevenlabs.io/docs/overview/models
- https://arxiv.org/abs/1609.03499 (WaveNet)
- https://arxiv.org/abs/1712.05884 (Tacotron 2)
