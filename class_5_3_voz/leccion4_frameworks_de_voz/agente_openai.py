"""Agente de voz con el OpenAI Agents SDK (RealtimeAgent) — voice-to-voice nativo.

El audio del micrófono va por un WebSocket a `gpt-realtime-2.1`, que **escucha y habla
directamente**: no hay transcripción ni síntesis en el medio. La detección de turnos
(`semantic_vad`) la hace el servidor, así que se puede interrumpir al agente hablando.

Lo que el SDK aporta sobre la API cruda: los mismos primitivos que ya conoces de los
agentes de texto — Agent, tools, handoffs, guardrails — más el manejo del protocolo.
Lo que NO aporta: la plomería de audio local. El micrófono y los parlantes los cableamos
nosotros con PyAudio, y por eso este archivo es el más largo de los tres.

Uso:
    uv run python agente_openai.py           # conversación por micrófono
    uv run python agente_openai.py --smoke   # solo verifica la sesión, sin micrófono
"""

import argparse
import asyncio
import sys

from dotenv import load_dotenv

from tienda import INSTRUCCIONES, consultar_stock

load_dotenv()

from agents import function_tool  # noqa: E402
from agents.realtime import RealtimeAgent, RealtimeRunner  # noqa: E402

MODELO = "gpt-realtime-2.1"
VOZ = "marin"

# La API Realtime trabaja con PCM16 crudo: 24 kHz mono en ambos sentidos.
TASA_MUESTREO = 24_000
TAMANO_BLOQUE = 1024


# ---------------------------------------------------------------------------
# La herramienta: la misma función de tienda.py, envuelta para el SDK
# ---------------------------------------------------------------------------

@function_tool
def consultar_stock_tool(nombre_producto: str) -> dict:
    """Consulta si un producto está disponible en la tienda y a qué precio.

    Args:
        nombre_producto: nombre del producto que preguntó el cliente.
    """
    resultado = consultar_stock(nombre_producto)
    print(f"   🔧 consultar_stock({nombre_producto!r}) → {resultado}")
    return resultado


agente = RealtimeAgent(
    name="Luis",
    instructions=INSTRUCCIONES,
    tools=[consultar_stock_tool],
)

CONFIGURACION = {
    "model_settings": {
        "model_name": MODELO,
        "audio": {
            "input": {
                "format": "pcm16",
                # El servidor decide cuándo terminó el turno del usuario. `semantic_vad`
                # usa el contenido, no solo el silencio: aguanta una pausa a mitad de frase.
                "turn_detection": {"type": "semantic_vad", "interrupt_response": True},
            },
            "output": {"format": "pcm16", "voice": VOZ},
        },
    },
}


# ---------------------------------------------------------------------------
# Modo smoke: verifica llave, modelo y sesión sin abrir el micrófono
# ---------------------------------------------------------------------------

async def smoke() -> int:
    """Abre la sesión, manda un mensaje de texto y confirma que llega audio de vuelta."""
    print(f"▶ Conectando a {MODELO} (sin micrófono)…")
    runner = RealtimeRunner(starting_agent=agente, config=CONFIGURACION)
    sesion = await runner.run()

    bytes_audio = 0
    async with sesion:
        await sesion.send_message("Hola, ¿tienen taladros?")

        async for evento in sesion:
            tipo = evento.type
            if tipo == "audio":
                bytes_audio += len(evento.audio.data)
            elif tipo == "tool_start":
                print(f"   🔧 el agente llamó a una herramienta")
            elif tipo == "history_updated" and evento.history:
                ultimo = evento.history[-1]
                for parte in getattr(ultimo, "content", None) or []:
                    texto = getattr(parte, "transcript", None) or getattr(parte, "text", None)
                    if texto:
                        print(f"   💬 {texto}")
            elif tipo == "agent_end":
                break
            elif tipo == "error":
                print(f"   ⛔ error: {evento}")
                return 1

    print(f"✓ Sesión OK · {bytes_audio:,} bytes de audio recibidos ({bytes_audio / (TASA_MUESTREO * 2):.1f}s)")
    return 0


# ---------------------------------------------------------------------------
# Modo conversación: micrófono y parlantes con PyAudio
# ---------------------------------------------------------------------------

async def conversar() -> int:
    import pyaudio

    audio = pyaudio.PyAudio()
    entrada = audio.open(format=pyaudio.paInt16, channels=1, rate=TASA_MUESTREO,
                         input=True, frames_per_buffer=TAMANO_BLOQUE)
    salida = audio.open(format=pyaudio.paInt16, channels=1, rate=TASA_MUESTREO,
                        output=True, frames_per_buffer=TAMANO_BLOQUE)

    print(f"▶ {MODELO} · voz {VOZ} · habla cuando quieras (Ctrl-C para salir)\n")

    runner = RealtimeRunner(starting_agent=agente, config=CONFIGURACION)
    sesion = await runner.run()

    async def enviar_microfono():
        """Lee el micrófono en bloques y lo empuja a la sesión."""
        while True:
            # read() es bloqueante: lo sacamos del event loop con un thread
            bloque = await asyncio.to_thread(
                entrada.read, TAMANO_BLOQUE, exception_on_overflow=False
            )
            await sesion.send_audio(bloque)

    async def recibir_eventos():
        """Reproduce el audio del agente y muestra lo que va pasando."""
        async for evento in sesion:
            tipo = evento.type
            if tipo == "audio":
                await asyncio.to_thread(salida.write, evento.audio.data)
            elif tipo == "audio_interrupted":
                # El usuario habló encima: el servidor ya cortó su turno.
                print("   ✋ (interrumpido)")
            elif tipo == "tool_start":
                pass  # el print lo hace la herramienta
            elif tipo == "history_updated" and evento.history:
                ultimo = evento.history[-1]
                rol = getattr(ultimo, "role", "?")
                for parte in getattr(ultimo, "content", None) or []:
                    texto = getattr(parte, "transcript", None) or getattr(parte, "text", None)
                    if texto:
                        etiqueta = "🧑 tú" if rol == "user" else "🤖 Luis"
                        print(f"{etiqueta}: {texto}")
            elif tipo == "error":
                print(f"⛔ {evento}")

    try:
        async with sesion:
            await asyncio.gather(enviar_microfono(), recibir_eventos())
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("\n▶ Cerrando…")
    finally:
        for flujo in (entrada, salida):
            flujo.stop_stream()
            flujo.close()
        audio.terminate()
    return 0


def main() -> int:
    analizador = argparse.ArgumentParser(description=__doc__)
    analizador.add_argument("--smoke", action="store_true",
                            help="verifica la sesión sin usar el micrófono")
    argumentos = analizador.parse_args()

    try:
        return asyncio.run(smoke() if argumentos.smoke else conversar())
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    sys.exit(main())
