"""Agente de voz con ElevenLabs Agents — la plataforma como producto.

La diferencia con los otros dos es de fondo, no de sintaxis: acá **el agente no vive en tu
código**. Se crea como un recurso en la plataforma de ElevenLabs (prompt, idioma, voz, modelo,
herramientas), y tu programa solo abre una conversación contra ese recurso y le presta el
micrófono. El prompt se puede editar desde el dashboard sin volver a desplegar nada.

Lo que ganas: no escribes nada de la plomería —turnos, interrupciones, audio, telefonía— y
tienes un panel con las conversaciones grabadas y transcritas. Lo que entregas: la lógica
conversacional queda en un proveedor, y sacarla de ahí después es un proyecto.

Las herramientas pueden ser *server tools* (la plataforma llama a tu API) o **client tools**
(la plataforma le pide a tu proceso que ejecute una función). Usamos client tools, que es el
equivalente más cercano a lo que hacen los otros dos scripts.

Uso:
    uv run python agente_elevenlabs.py           # crea el agente, conversa, y lo borra al salir
    uv run python agente_elevenlabs.py --check   # crea el agente, lo verifica y lo borra
    uv run python agente_elevenlabs.py --conservar   # no lo borra (para verlo en el dashboard)
"""

import argparse
import os
import signal
import sys

from dotenv import load_dotenv

from tienda import CATALOGO, INSTRUCCIONES, consultar_stock

load_dotenv()

# El material antiguo del curso usaba ELEVEN_API_KEY; el SDK actual espera ELEVENLABS_API_KEY.
if not os.environ.get("ELEVENLABS_API_KEY") and os.environ.get("ELEVEN_API_KEY"):
    os.environ["ELEVENLABS_API_KEY"] = os.environ["ELEVEN_API_KEY"]

from elevenlabs.client import ElevenLabs  # noqa: E402
from elevenlabs.conversational_ai.conversation import ClientTools, Conversation  # noqa: E402
from elevenlabs.conversational_ai.default_audio_interface import (  # noqa: E402
    DefaultAudioInterface,
)

# Voz "premade": funciona en el plan gratis. Las voces de la biblioteca de la comunidad
# —incluidas las de acento chileno— requieren plan pago (ver la lección 2).
VOZ = "JBFqnCBsd6RMkjVDRZzb"  # George
# Un agente en español debe usar turbo o flash v2_5: la API rechaza los demás modelos.
MODELO_TTS = "eleven_flash_v2_5"
MODELO_LLM = "gpt-4o-mini"


def crear_agente(cliente: ElevenLabs) -> str:
    """Crea el agente en la plataforma y devuelve su id."""
    # Nota: la herramienta se declara acá, en la *configuración del recurso*, no en el
    # código. La plataforma decide cuándo llamarla y le pide a nuestro proceso que la corra.
    creado = cliente.conversational_ai.agents.create(
        name="Luis · Ferretería Central (clase 5.3)",
        conversation_config={
            "agent": {
                "prompt": {
                    "prompt": INSTRUCCIONES,
                    "llm": MODELO_LLM,
                    "tools": [
                        {
                            "type": "client",
                            "name": "consultar_stock",
                            "description": (
                                "Consulta si un producto está disponible en la tienda "
                                "y a qué precio."
                            ),
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
                "first_message": "Hola, Ferretería Central, habla Luis. ¿En qué le puedo ayudar?",
                "language": "es",
            },
            "tts": {"model_id": MODELO_TTS, "voice_id": VOZ},
        },
    )
    return creado.agent_id


def armar_herramientas() -> ClientTools:
    """Registra la función local que la plataforma va a invocar."""
    herramientas = ClientTools()

    def manejar(parametros: dict):
        nombre = parametros.get("nombre_producto", "")
        resultado = consultar_stock(nombre)
        print(f"   🔧 consultar_stock({nombre!r}) → {resultado}")
        return resultado

    herramientas.register("consultar_stock", manejar)
    return herramientas


def conversar(cliente: ElevenLabs, agent_id: str) -> None:
    conversacion = Conversation(
        cliente,
        agent_id,
        # El agente es nuestro y la llave está en el entorno, así que la sesión va firmada.
        requires_auth=True,
        audio_interface=DefaultAudioInterface(),  # micrófono y parlantes del sistema
        client_tools=armar_herramientas(),
        callback_user_transcript=lambda texto: print(f"🧑 tú   : {texto}"),
        callback_agent_response=lambda texto: print(f"🤖 Luis : {texto}"),
        callback_latency_measurement=lambda ms: print(f"   ⏱️  {ms} ms"),
    )

    print(f"▶ ElevenLabs Agents · {agent_id}")
    print(f"  LLM {MODELO_LLM} · TTS {MODELO_TTS} · habla cuando quieras (Ctrl-C para salir)\n")

    # Ctrl-C termina la sesión de forma ordenada en vez de matar el proceso.
    signal.signal(signal.SIGINT, lambda *_: conversacion.end_session())

    conversacion.start_session()
    conversacion.wait_for_session_end()


def main() -> int:
    analizador = argparse.ArgumentParser(description=__doc__)
    analizador.add_argument("--check", action="store_true",
                            help="crea el agente, lo verifica y lo borra, sin micrófono")
    analizador.add_argument("--conservar", action="store_true",
                            help="no borrar el agente al terminar (para verlo en el dashboard)")
    argumentos = analizador.parse_args()

    if not os.environ.get("ELEVENLABS_API_KEY"):
        print("⛔ Falta ELEVENLABS_API_KEY (crea una llave gratis en elevenlabs.io).")
        return 1

    cliente = ElevenLabs()

    print("▶ Creando el agente en la plataforma…")
    agent_id = crear_agente(cliente)
    print(f"  agent_id: {agent_id}")

    try:
        if argumentos.check:
            agente = cliente.conversational_ai.agents.get(agent_id)
            print(f"✓ Agente creado y accesible: {agente.name!r}")
            print(f"  catálogo local con {len(CATALOGO)} productos listo para la client tool.")
            print("  (no se abrió el micrófono)")
        else:
            conversar(cliente, agent_id)
    finally:
        if argumentos.conservar:
            print(f"\n▶ Agente conservado: https://elevenlabs.io/app/agents/{agent_id}")
        else:
            cliente.conversational_ai.agents.delete(agent_id)
            print("\n▶ Agente borrado de la plataforma.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
