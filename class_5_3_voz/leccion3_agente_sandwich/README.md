# leccion3_agente_sandwich

**Un agente con el que se puede conversar**, armado con el método **sándwich** (o cascada):

```
🎙️  audio  ──▶  STT  ──▶  texto  ──▶  AGENTE  ──▶  texto  ──▶  TTS  ──▶  audio  🔊
              lección 1                (+ herramientas)         lección 2
```

Tercera lección de la Clase 5.3. Junta las dos anteriores alrededor de un agente de texto de
LangChain 1.x, mide el costo en latencia de encadenar tres modelos, y termina nombrando los
tres límites que esta arquitectura **no** puede superar — que son la razón de existir de la
lección 4.

## Qué hace

| Paso | Detalle |
|---|---|
| Setup | Carga `OPENAI_API_KEY` y `TAVILY_API_KEY` desde Colab userdata o `.env`. |
| El agente | `create_agent` (LangChain 1.x) + `TavilySearch`, con un system prompt escrito **para voz**: sin listas, sin markdown, sin URLs, 2-3 frases, cifras como se pronuncian. |
| Elección de modelo | Cuatro configuraciones cronometradas sobre la misma pregunta con búsqueda web. |
| Las tres capas | `escuchar()` (`gpt-transcribe`) → `pensar()` (agente) → `responder()` (`gpt-4o-mini-tts`), y `conversar()` que las encadena instrumentando cada tramo. |
| Un turno completo | La pregunta del usuario se **fabrica con TTS** para poder probar el pipeline sin micrófono — útil también para testear agentes de voz de forma automatizada. |
| Presupuesto | Tabla con el aporte de cada capa al tiempo que el usuario espera. |
| Interfaz | Gradio con micrófono (`prevent_thread_lock=True`, más una celda que cierra el servidor). |

## Los dos hallazgos que la lección usa como contenido

**1. El modelo del medio se elige por latencia, no por ranking.** Medido sobre la misma
pregunta: `gpt-5-mini` con razonamiento por defecto se toma **decenas de segundos** y encadena
hasta nueve búsquedas; `gpt-4.1-mini` responde en ~5 s. La referencia es que en una
conversación humana el turno cambia en ~200 ms.

Y no es un almuerzo gratis: en varias corridas **el modelo lento fue el único que consiguió el
dato exacto**, precisamente porque insistió. Se está cambiando calidad por tiempo, y la lección
lo dice explícitamente en vez de vender el modelo rápido como superior.

**2. La capa que más pesa es el TTS, no el agente.** Consistentemente ~55-58% del total
(vs. ~20% del agente). Es un buen argumento para instrumentar antes de optimizar, y conecta
directo con el modelo `flash` que medimos en la lección 2.

## Requisitos

- Python 3.12 y [uv](https://github.com/astral-sh/uv), o Google Colab.
- **API key de OpenAI**: https://platform.openai.com — obligatoria, las tres capas son de OpenAI.
- **API key de Tavily** (opcional): https://tavily.com — plan gratis de 1.000 búsquedas/mes.
  Sin ella el agente funciona igual, solo sin buscar en internet.
- Un **micrófono** para la parte de Gradio. El resto del notebook corre sin micrófono, porque
  el audio de entrada se sintetiza.

## Configuración

```bash
# 1. Copia la plantilla de secretos y completa tus llaves
cp .env.example .env          # edita OPENAI_API_KEY (y TAVILY_API_KEY si tienes)

# 2. Sincroniza el entorno (crea .venv con las dependencias fijadas)
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
```

## Ejecución local

```bash
# Registra el kernel de Jupyter para este entorno
uv run python -m ipykernel install --user \
  --name clase-5-3-l3 --display-name "Python (clase 5.3 · L3)"

# Abre el notebook
uv run --with jupyterlab jupyter lab agente_de_voz_sandwich.ipynb
```

La celda de Gradio imprime una URL local (`http://127.0.0.1:7860`): ábrela, graba y escucha.
Al terminar, corre la celda siguiente para cerrar el servidor y liberar el puerto.

Los audios de cada turno quedan en `outputs/` (git-ignorado).

## Notas sobre APIs que cambiaron

- `create_agent` reemplaza al par `create_tool_calling_agent` + `AgentExecutor`, y se invoca
  con `{"messages": [...]}`.
- La herramienta de Tavily vive en **`langchain-tavily`** (`TavilySearch`); la vieja
  `TavilySearchResults` de `langchain_community` está deprecada.
- El material original usaba **`ipywebrtc`** para grabar dentro del notebook, que ya no
  funciona en los Jupyter/Colab actuales. Se reemplazó por Gradio, que además funciona igual
  en local y en Colab.

## Referencias

- https://docs.langchain.com/oss/python/langchain/agents
- https://developers.openai.com/api/docs/guides/voice-agents
- https://www.gradio.app/docs/gradio/audio
