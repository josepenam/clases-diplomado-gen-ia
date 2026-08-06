"""Nivel 0: la API Realtime directa, sin framework.

Este script existe para responder una pregunta concreta: **¿qué están haciendo por mí los
frameworks?** Acá no hay abstracciones — se abre un WebSocket a `/v1/realtime`, se configura
la sesión con un JSON, se empujan bloques de audio en base64 y se van interpretando a mano
los eventos que llegan.

Es el punto de partida del material original de esta clase (`openai_realtime.py`), recortado
a lo mínimo y actualizado a la forma actual de la API. Compáralo con `agente_openai.py`: hace
menos, en más líneas.

Uso:
    uv run python nivel0_websocket_crudo.py           # conversación por micrófono
    uv run python nivel0_websocket_crudo.py --smoke   # solo el handshake, sin micrófono
"""

import argparse
import asyncio
import base64
import json
import os
import sys

from dotenv import load_dotenv

from tienda import INSTRUCCIONES, consultar_stock

load_dotenv()

import websockets  # noqa: E402

MODELO = "gpt-realtime-2.1"
URL = f"wss://api.openai.com/v1/realtime?model={MODELO}"
TASA_MUESTREO = 24_000
TAMANO_BLOQUE = 1024

# Toda la configuración de la sesión es este diccionario. Ojo con la forma: cambió respecto
# a la API de 2024 (antes era `input_audio_format: "pcm16"` y `turn_detection` al tope; hoy
# todo vive anidado bajo `audio.input` / `audio.output`).
SESION = {
    "type": "session.update",
    "session": {
        "type": "realtime",
        "instructions": INSTRUCCIONES,
        "output_modalities": ["audio"],
        "audio": {
            "input": {
                "format": {"type": "audio/pcm", "rate": TASA_MUESTREO},
                "transcription": {"model": "gpt-4o-mini-transcribe"},
                "turn_detection": {"type": "semantic_vad", "interrupt_response": True},
                "noise_reduction": {"type": "near_field"},
            },
            "output": {"format": {"type": "audio/pcm", "rate": TASA_MUESTREO}, "voice": "marin"},
        },
        "tools": [
            {
                "type": "function",
                "name": "consultar_stock",
                "description": "Consulta si un producto está disponible y a qué precio.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "nombre_producto": {
                            "type": "string",
                            "description": "Producto que preguntó el cliente.",
                        }
                    },
                    "required": ["nombre_producto"],
                },
            }
        ],
    },
}


async def conectar():
    return await websockets.connect(
        URL, additional_headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"}
    )


async def responder_herramienta(ws, call_id: str, argumentos_json: str) -> None:
    """Ejecuta la función y devuelve el resultado — a mano, en dos mensajes."""
    argumentos = json.loads(argumentos_json or "{}")
    resultado = consultar_stock(argumentos.get("nombre_producto", ""))
    print(f"   🔧 consultar_stock({argumentos.get('nombre_producto')!r}) → {resultado}")

    # 1. entregar la salida de la función…
    await ws.send(json.dumps({
        "type": "conversation.item.create",
        "item": {
            "type": "function_call_output",
            "call_id": call_id,
            "output": json.dumps(resultado, ensure_ascii=False),
        },
    }))
    # 2. …y pedirle explícitamente que siga hablando. Los frameworks hacen estos dos
    #    pasos por ti; si te olvidas del segundo, el agente se queda mudo.
    await ws.send(json.dumps({"type": "response.create"}))


async def manejar_eventos(ws, escribir_audio=None, interrumpir=None) -> None:
    """Bucle de eventos. Esto es lo que un framework te esconde."""
    async for crudo in ws:
        evento = json.loads(crudo)
        tipo = evento["type"]

        if tipo == "response.output_audio.delta":
            if escribir_audio:
                escribir_audio(base64.b64decode(evento["delta"]))

        elif tipo == "response.output_audio_transcript.done":
            print(f"🤖 Luis : {evento['transcript']}")

        elif tipo == "conversation.item.input_audio_transcription.completed":
            print(f"🧑 tú   : {evento['transcript']}")

        elif tipo == "response.function_call_arguments.done":
            await responder_herramienta(ws, evento["call_id"], evento["arguments"])

        elif tipo == "input_audio_buffer.speech_started":
            # Botamos el audio pendiente: el servidor ya cortó su turno.
            if interrumpir:
                interrumpir()
            print("   ✋ (hablaste: se interrumpe)")

        elif tipo == "error":
            print(f"⛔ {evento['error']}")


async def smoke() -> int:
    print(f"▶ Handshake con {MODELO} (sin micrófono)…")
    async with await conectar() as ws:
        creada = json.loads(await ws.recv())
        print(f"  ← {creada['type']} · sesión {creada['session']['id']}")

        await ws.send(json.dumps(SESION))
        await ws.send(json.dumps({
            "type": "conversation.item.create",
            "item": {"type": "message", "role": "user",
                     "content": [{"type": "input_text", "text": "¿Tienen taladros?"}]},
        }))
        await ws.send(json.dumps({"type": "response.create"}))

        bytes_audio = 0
        async for crudo in ws:
            evento = json.loads(crudo)
            if evento["type"] == "response.output_audio.delta":
                bytes_audio += len(base64.b64decode(evento["delta"]))
            elif evento["type"] == "response.function_call_arguments.done":
                await responder_herramienta(ws, evento["call_id"], evento["arguments"])
            elif evento["type"] == "response.output_audio_transcript.done":
                print(f"  💬 {evento['transcript']}")
            elif evento["type"] == "response.done":
                if bytes_audio:
                    break
            elif evento["type"] == "error":
                print(f"  ⛔ {evento['error']}")
                return 1

    print(f"✓ Handshake OK · {bytes_audio:,} bytes de audio ({bytes_audio / (TASA_MUESTREO * 2):.1f}s)")
    return 0


async def conversar() -> int:
    import pyaudio

    from salida_fluida import ReproductorFluido

    audio = pyaudio.PyAudio()
    entrada = audio.open(format=pyaudio.paInt16, channels=1, rate=TASA_MUESTREO,
                         input=True, frames_per_buffer=TAMANO_BLOQUE)
    # Los deltas llegan a ráfagas; escribirlos directo al dispositivo suena a saltos.
    reproductor = ReproductorFluido(tasa=TASA_MUESTREO, py_audio=audio)
    reproductor.iniciar()

    print(f"▶ {MODELO} sin framework · habla cuando quieras (Ctrl-C para salir)\n")

    async with await conectar() as ws:
        await ws.recv()                      # session.created
        await ws.send(json.dumps(SESION))    # nuestra configuración

        async def enviar():
            while True:
                bloque = await asyncio.to_thread(
                    entrada.read, TAMANO_BLOQUE, exception_on_overflow=False
                )
                await ws.send(json.dumps({
                    "type": "input_audio_buffer.append",
                    "audio": base64.b64encode(bloque).decode(),
                }))

        try:
            await asyncio.gather(
                enviar(),
                manejar_eventos(ws, reproductor.escribir, reproductor.interrumpir),
            )
        finally:
            entrada.stop_stream()
            entrada.close()
            reproductor.detener()
            audio.terminate()
    return 0


def main() -> int:
    analizador = argparse.ArgumentParser(description=__doc__)
    analizador.add_argument("--smoke", action="store_true", help="solo el handshake")
    argumentos = analizador.parse_args()
    try:
        return asyncio.run(smoke() if argumentos.smoke else conversar())
    except KeyboardInterrupt:
        print("\n▶ Cerrando…")
        return 0


if __name__ == "__main__":
    sys.exit(main())
