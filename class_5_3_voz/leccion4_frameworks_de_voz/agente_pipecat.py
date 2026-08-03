"""Agente de voz con Pipecat (open source, de Daily) — el pipeline explícito.

La idea de Pipecat es que la conversación es un **pipeline de frames**: el audio entra por
un extremo, atraviesa una lista de procesadores y sale por el otro. Eso hace que las dos
arquitecturas de esta clase sean literalmente la misma lista con dos elementos de diferencia,
y por eso este script implementa las dos:

    --modo cascada    input → STT → contexto → LLM → TTS → output     (la lección 3)
    --modo realtime   input → contexto → LLM(voice-to-voice) → output (la lección 4)

En `realtime` desaparecen el STT y el TTS: el servicio de LLM **es** el modelo de voz.
Poder cambiar de arquitectura moviendo dos líneas es el argumento central de Pipecat, y
también es lo que permite cambiar de proveedor sin tocar el resto (Deepgram por OpenAI,
ElevenLabs por Cartesia, etc.).

Uso:
    uv run python agente_pipecat.py                  # voice-to-voice (por defecto)
    uv run python agente_pipecat.py --modo cascada   # el sándwich, para comparar
    uv run python agente_pipecat.py --check          # arma el pipeline y sale, sin micrófono
"""

import argparse
import asyncio
import os
import sys

from dotenv import load_dotenv

load_dotenv()

# Pipecat importa nltk, que trae un hook de seguridad que bloquea cualquier módulo cuyo
# origen esté dentro del directorio de trabajo. Como nuestro `.venv` vive justamente ahí
# (convención de uv), ese hook rompe el import. Hay que desactivarlo ANTES de importar
# pipecat. Ver el README de la lección.
os.environ.setdefault("NLTK_DISABLE_IMPORT_SECURITY", "1")

from pipecat.adapters.schemas.function_schema import FunctionSchema  # noqa: E402
from pipecat.adapters.schemas.tools_schema import ToolsSchema  # noqa: E402
from pipecat.audio.vad.silero import SileroVADAnalyzer  # noqa: E402
from pipecat.pipeline.pipeline import Pipeline  # noqa: E402
from pipecat.pipeline.runner import WorkerRunner  # noqa: E402
from pipecat.pipeline.task import PipelineParams  # noqa: E402
from pipecat.pipeline.worker import PipelineWorker  # noqa: E402
from pipecat.processors.aggregators.llm_context import LLMContext  # noqa: E402
from pipecat.processors.aggregators.llm_response_universal import (  # noqa: E402
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.services.llm_service import FunctionCallParams  # noqa: E402
from pipecat.transports.local.audio import (  # noqa: E402
    LocalAudioTransport,
    LocalAudioTransportParams,
)

from tienda import INSTRUCCIONES, consultar_stock  # noqa: E402

MODELO_REALTIME = "gpt-realtime-2.1"
MODELO_CASCADA = "gpt-4.1-mini"       # el mismo de la lección 3: elegido por latencia
MODELO_STT = "gpt-transcribe"
MODELO_TTS = "gpt-4o-mini-tts"
VOZ = "marin"


# ---------------------------------------------------------------------------
# La herramienta, declarada de forma agnóstica al proveedor
# ---------------------------------------------------------------------------

ESQUEMA_STOCK = FunctionSchema(
    name="consultar_stock",
    description="Consulta si un producto está disponible en la tienda y a qué precio.",
    properties={
        "nombre_producto": {
            "type": "string",
            "description": "Nombre del producto que preguntó el cliente.",
        }
    },
    required=["nombre_producto"],
)


async def manejar_consultar_stock(params: FunctionCallParams) -> None:
    """Handler de Pipecat: recibe los argumentos y devuelve el resultado por callback."""
    nombre = params.arguments.get("nombre_producto", "")
    resultado = consultar_stock(nombre)
    print(f"   🔧 consultar_stock({nombre!r}) → {resultado}")
    await params.result_callback(resultado)


# ---------------------------------------------------------------------------
# Armado del pipeline
# ---------------------------------------------------------------------------

def construir(modo: str) -> tuple[Pipeline, PipelineWorker]:
    """Devuelve el pipeline y su worker para el modo pedido."""
    transporte = LocalAudioTransport(
        LocalAudioTransportParams(audio_in_enabled=True, audio_out_enabled=True)
    )

    herramientas = ToolsSchema(standard_tools=[ESQUEMA_STOCK])
    contexto = LLMContext(messages=[], tools=herramientas)

    # El VAD decide cuándo terminó de hablar el usuario. Silero corre **local**: no manda
    # el audio a ningún servidor para detectar silencios.
    agregador_usuario, agregador_asistente = LLMContextAggregatorPair(
        contexto,
        user_params=LLMUserAggregatorParams(vad_analyzer=SileroVADAnalyzer()),
    )

    if modo == "realtime":
        from pipecat.services.openai.realtime.events import (
            AudioConfiguration,
            AudioInput,
            InputAudioNoiseReduction,
            InputAudioTranscription,
            SemanticTurnDetection,
            SessionProperties,
        )
        from pipecat.services.openai.realtime.llm import OpenAIRealtimeLLMService

        propiedades = SessionProperties(
            audio=AudioConfiguration(
                input=AudioInput(
                    # La transcripción acá es solo para que TÚ puedas loguear y evaluar:
                    # el modelo no la necesita para responder, oye el audio directo.
                    transcription=InputAudioTranscription(),
                    turn_detection=SemanticTurnDetection(),
                    noise_reduction=InputAudioNoiseReduction(type="near_field"),
                )
            ),
        )

        llm = OpenAIRealtimeLLMService(
            api_key=os.environ["OPENAI_API_KEY"],
            settings=OpenAIRealtimeLLMService.Settings(
                model=MODELO_REALTIME,
                session_properties=propiedades,
                system_instruction=INSTRUCCIONES,
            ),
        )
        llm.register_function("consultar_stock", manejar_consultar_stock)

        # Sin STT y sin TTS: el LLM oye y habla.
        etapas = [
            transporte.input(),
            agregador_usuario,
            llm,
            transporte.output(),
            agregador_asistente,
        ]
    else:
        from pipecat.services.openai.llm import OpenAILLMService
        from pipecat.services.openai.stt import OpenAISTTService
        from pipecat.services.openai.tts import OpenAITTSService

        # En Pipecat 1.7 la configuración va en `settings=...`; pasar `model=`/`voice=`
        # directo al constructor todavía funciona pero está deprecado.
        stt = OpenAISTTService(settings=OpenAISTTService.Settings(model=MODELO_STT))
        tts = OpenAITTSService(settings=OpenAITTSService.Settings(model=MODELO_TTS, voice=VOZ))
        llm = OpenAILLMService(settings=OpenAILLMService.Settings(model=MODELO_CASCADA))
        llm.register_function("consultar_stock", manejar_consultar_stock)

        contexto.add_message({"role": "system", "content": INSTRUCCIONES})

        # Las dos etapas extra son exactamente el "pan" del sándwich.
        etapas = [
            transporte.input(),
            stt,
            agregador_usuario,
            llm,
            tts,
            transporte.output(),
            agregador_asistente,
        ]

    pipeline = Pipeline(etapas)
    worker = PipelineWorker(
        pipeline,
        params=PipelineParams(enable_metrics=True, enable_usage_metrics=True),
    )
    return pipeline, worker


def describir(modo: str, pipeline: Pipeline) -> None:
    print(f"▶ Pipecat · modo {modo}")
    nombres = [type(p).__name__ for p in pipeline.processors]
    print("  " + " → ".join(nombres))
    if modo == "realtime":
        print(f"  modelo: {MODELO_REALTIME} (oye y habla; sin STT ni TTS)")
    else:
        print(f"  modelos: {MODELO_STT} → {MODELO_CASCADA} → {MODELO_TTS}")


async def ejecutar(modo: str) -> int:
    pipeline, worker = construir(modo)
    describir(modo, pipeline)
    print("  habla cuando quieras (Ctrl-C para salir)\n")

    runner = WorkerRunner(handle_sigint=False)
    await runner.add_workers(worker)
    await runner.run()
    return 0


def main() -> int:
    analizador = argparse.ArgumentParser(description=__doc__)
    analizador.add_argument("--modo", choices=("realtime", "cascada"), default="realtime",
                            help="voice-to-voice nativo (por defecto) o el sándwich")
    analizador.add_argument("--check", action="store_true",
                            help="arma el pipeline y sale, sin abrir el micrófono")
    argumentos = analizador.parse_args()

    if argumentos.check:
        pipeline, _ = construir(argumentos.modo)
        describir(argumentos.modo, pipeline)
        print("\n✓ Pipeline armado correctamente (no se abrió el micrófono).")
        return 0

    try:
        return asyncio.run(ejecutar(argumentos.modo))
    except KeyboardInterrupt:
        print("\n▶ Cerrando…")
        return 0


if __name__ == "__main__":
    sys.exit(main())
