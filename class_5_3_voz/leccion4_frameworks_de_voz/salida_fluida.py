"""Salida de audio con jitter buffer, para que la reproducción local no salga a saltos.

## El problema

Tanto el `LocalAudioTransport` de Pipecat como el `DefaultAudioInterface` de ElevenLabs
escriben al dispositivo con `stream.write()` **bloqueante**, entregando trozos cortos
(40 ms en Pipecat) uno tras otro. Eso deja al dispositivo casi sin cojín: en cuanto el
productor se retrasa unos milisegundos —y en un proceso que además corre VAD, STT, LLM y
TTS en el mismo event loop, se retrasa— el parlante se queda sin datos y se oye un
microcorte.

Medido con `stream.write(..., exception_on_underflow=True)` sobre el camino real de Pipecat:
**el 100% de los writes reportaba underflow**, unos 22 por segundo. Eso es el audio "saltón".

## La solución

La de siempre en audio en tiempo real: **desacoplar** la llegada de los datos de su
reproducción con un *ring buffer* y un stream en modo **callback**. El dispositivo pide
audio cuando lo necesita y se sirve del buffer; el productor solo deposita. Con un
pre-buffer de unos 200 ms, el audio aguanta huecos de red de más de un segundo sin cortarse
(la API Realtime entrega a ~1,9× tiempo real, así que el buffer acumula ventaja).

Este módulo trae dos piezas:

- `ReproductorFluido` — el ring buffer + stream de callback, usable por sí solo.
- `SalidaFluidaTransport` / `transporte_local_fluido()` — un `LocalAudioTransport` de Pipecat
  con la salida reemplazada por el reproductor de arriba.

Para ElevenLabs, `InterfazAudioFluida` hace lo mismo sobre su `DefaultAudioInterface`.

## Comprobarlo en tu máquina

    uv run python salida_fluida.py

Sintetiza una frase con TTS y la reproduce por las dos rutas —la original de Pipecat y la
bufferizada— contando los underflows que reporta PortAudio en cada una.
"""

from __future__ import annotations

import threading

import pyaudio


class ReproductorFluido:
    """Reproductor con ring buffer y stream en modo callback.

    El dispositivo tira del buffer a su propio ritmo; `escribir()` solo deposita y
    nunca bloquea. La reproducción no arranca hasta juntar `prebuffer_ms`, para no
    empezar a sonar con el buffer en cero.
    """

    def __init__(
        self,
        tasa: int = 24_000,
        canales: int = 1,
        prebuffer_ms: int = 200,
        indice_dispositivo: int | None = None,
        py_audio: pyaudio.PyAudio | None = None,
    ):
        self.tasa = tasa
        self.canales = canales
        self._bytes_por_segundo = tasa * canales * 2
        self._objetivo_prebuffer = int(self._bytes_por_segundo * prebuffer_ms / 1000)

        self._py_audio = py_audio or pyaudio.PyAudio()
        self._propietario_pyaudio = py_audio is None
        self._indice = indice_dispositivo

        self._buffer = bytearray()
        self._cerrojo = threading.Lock()
        self._sonando = False
        self._stream: pyaudio.Stream | None = None

        # Diagnóstico. `underruns` = el buffer se secó a media frase (corte audible).
        # `underflows_portaudio` = la misma señal que PortAudio reporta con
        # `exception_on_underflow`, para poder comparar contra la salida original.
        self.underruns = 0
        self.underflows_portaudio = 0
        self.callbacks = 0

    # ------------------------------------------------------------------
    def _callback(self, in_data, frame_count, time_info, status):
        piden = frame_count * self.canales * 2
        self.callbacks += 1
        if status & pyaudio.paOutputUnderflow:
            self.underflows_portaudio += 1
        with self._cerrojo:
            disponible = len(self._buffer)

            if not self._sonando:
                # Todavía juntando el pre-buffer, o entre turnos: silencio, sin contar nada.
                return (b"\x00" * piden, pyaudio.paContinue)

            if disponible >= piden:
                datos = bytes(self._buffer[:piden])
                del self._buffer[:piden]
            elif disponible > 0:
                # Se quedó seco A MEDIA frase: esto sí es un corte audible.
                self.underruns += 1
                datos = bytes(self._buffer) + b"\x00" * (piden - disponible)
                self._buffer.clear()
                self._sonando = False  # vuelve a pre-bufferear
            else:
                # Buffer vacío y sin nada pendiente: terminó el turno, no es un corte.
                self._sonando = False
                datos = b"\x00" * piden

        return (datos, pyaudio.paContinue)

    def iniciar(self) -> None:
        if self._stream is not None:
            return
        # Un buffer de dispositivo holgado (~85 ms) reduce la presión sobre el callback.
        self._stream = self._py_audio.open(
            format=pyaudio.paInt16,
            channels=self.canales,
            rate=self.tasa,
            output=True,
            output_device_index=self._indice,
            frames_per_buffer=2048,
            stream_callback=self._callback,
        )
        self._stream.start_stream()

    def escribir(self, audio: bytes) -> None:
        """Deposita audio en el buffer. No bloquea nunca."""
        with self._cerrojo:
            self._buffer.extend(audio)
            if not self._sonando and len(self._buffer) >= self._objetivo_prebuffer:
                self._sonando = True

    def interrumpir(self) -> None:
        """Bota el audio pendiente (el usuario habló encima)."""
        with self._cerrojo:
            self._buffer.clear()
            self._sonando = False  # vuelve a pre-bufferear en el turno siguiente

    def detener(self) -> None:
        if self._stream is not None:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None
        if self._propietario_pyaudio:
            self._py_audio.terminate()


# ----------------------------------------------------------------------
# Pipecat
# ----------------------------------------------------------------------

def transporte_local_fluido(params, prebuffer_ms: int = 200):
    """Devuelve un `LocalAudioTransport` de Pipecat con la salida bufferizada.

    Se usa igual que `LocalAudioTransport(params)`; solo cambia que el audio de salida
    pasa por un ring buffer en vez de escribirse trozo a trozo al dispositivo.
    """
    from pipecat.frames.frames import OutputAudioRawFrame, StartFrame
    from pipecat.transports.local.audio import (
        LocalAudioOutputTransport,
        LocalAudioTransport,
    )

    class SalidaLocalFluida(LocalAudioOutputTransport):
        async def start(self, frame: StartFrame):
            # Saltamos el `start` de LocalAudioOutputTransport (que abre el stream
            # bloqueante) y llamamos al de su padre.
            await super(LocalAudioOutputTransport, self).start(frame)
            if getattr(self, "_reproductor", None) is None:
                tasa = self._params.audio_out_sample_rate or frame.audio_out_sample_rate
                self._reproductor = ReproductorFluido(
                    tasa=tasa,
                    canales=self._params.audio_out_channels,
                    prebuffer_ms=prebuffer_ms,
                    indice_dispositivo=self._params.output_device_index,
                    py_audio=self._py_audio,
                )
                self._reproductor.iniciar()
            await self.set_transport_ready(frame)

        async def write_audio_frame(self, frame: OutputAudioRawFrame) -> bool:
            reproductor = getattr(self, "_reproductor", None)
            if reproductor is None:
                return False
            reproductor.escribir(frame.audio)
            return True

        async def _start_interruption(self):
            await super()._start_interruption()
            reproductor = getattr(self, "_reproductor", None)
            if reproductor is not None:
                reproductor.interrumpir()

        async def cleanup(self):
            await super(LocalAudioOutputTransport, self).cleanup()
            reproductor = getattr(self, "_reproductor", None)
            if reproductor is not None:
                # Se detiene pero NO se descarta: sus contadores sirven para diagnosticar
                # después de cerrar el pipeline.
                reproductor.detener()

    class TransporteLocalFluido(LocalAudioTransport):
        def output(self):
            if not self._output:
                self._output = SalidaLocalFluida(self._pyaudio, self._params)
            return self._output

    return TransporteLocalFluido(params)


# ----------------------------------------------------------------------
# ElevenLabs
# ----------------------------------------------------------------------

def InterfazAudioFluida(prebuffer_ms: int = 200):
    """`DefaultAudioInterface` de ElevenLabs con la salida bufferizada.

    Su implementación original ya usa una cola y un thread propio —el diseño correcto—
    pero escribe con `write()` bloqueante sobre un buffer de dispositivo chico
    (62,5 ms), así que igual se queda corta cuando el proceso se retrasa. Acá la salida
    pasa por el mismo ring buffer con callback.

    Se pasa a `Conversation(..., audio_interface=InterfazAudioFluida())`.
    """
    from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface

    class _InterfazFluida(DefaultAudioInterface):
        # ElevenLabs negocia pcm_16000 en las dos direcciones.
        TASA = 16_000

        def start(self, input_callback):
            super().start(input_callback)
            self._reproductor = ReproductorFluido(
                tasa=self.TASA, prebuffer_ms=prebuffer_ms, py_audio=self.p
            )
            self._reproductor.iniciar()

        def output(self, audio: bytes):
            self._reproductor.escribir(audio)

        def interrupt(self):
            super().interrupt()
            self._reproductor.interrumpir()

        def stop(self):
            self._reproductor.detener()
            super().stop()

    return _InterfazFluida()


# ----------------------------------------------------------------------
# Diagnóstico: python salida_fluida.py
# ----------------------------------------------------------------------

_FRASE = (
    "Buenas tardes, habla Luis de Ferretería Central. Tenemos taladros disponibles, "
    "doce unidades, a cincuenta y cuatro mil novecientos noventa pesos. "
    "También hay martillos, cemento y pintura blanca."
)
_TASA = 24_000


def _reproducir_una_vez(bufferizada: bool) -> None:
    """Sintetiza la frase y la reproduce por una de las dos rutas, contando underflows.

    Corre en su propio proceso: dos pipelines de Pipecat en el mismo proceso se pisan.
    """
    import asyncio
    import os

    os.environ.setdefault("NLTK_DISABLE_IMPORT_SECURITY", "1")
    from dotenv import load_dotenv

    load_dotenv()
    from loguru import logger

    logger.remove()

    from pipecat.frames.frames import EndFrame, TTSSpeakFrame
    from pipecat.pipeline.pipeline import Pipeline
    from pipecat.pipeline.runner import WorkerRunner
    from pipecat.pipeline.task import PipelineParams
    from pipecat.pipeline.worker import PipelineWorker
    from pipecat.services.openai.tts import OpenAITTSService
    from pipecat.transports.local.audio import (
        LocalAudioTransport,
        LocalAudioTransportParams,
    )

    parametros = LocalAudioTransportParams(
        audio_in_enabled=False, audio_out_enabled=True, audio_out_sample_rate=_TASA
    )

    # En la ruta original interceptamos los write() bloqueantes con
    # exception_on_underflow=True: es la misma señal que el flag paOutputUnderflow del
    # callback, así que las dos mediciones son comparables.
    cuenta = {"writes": 0, "underflows": 0}
    if not bufferizada:
        _open_real = pyaudio.PyAudio.open

        def _open_espia(self, *a, **kw):
            stream = _open_real(self, *a, **kw)
            if kw.get("output") and not kw.get("stream_callback"):
                _write = stream.write

                def _write_espia(data, *aa, **kk):
                    cuenta["writes"] += 1
                    try:
                        return _write(data, exception_on_underflow=True)
                    except OSError:
                        cuenta["underflows"] += 1

                stream.write = _write_espia
            return stream

        pyaudio.PyAudio.open = _open_espia
        transporte = LocalAudioTransport(parametros)
    else:
        transporte = transporte_local_fluido(parametros)

    salida = transporte.output()

    async def correr():
        tts = OpenAITTSService(
            settings=OpenAITTSService.Settings(model="gpt-4o-mini-tts", voice="marin")
        )
        worker = PipelineWorker(
            Pipeline([tts, salida]), params=PipelineParams(audio_out_sample_rate=_TASA)
        )
        runner = WorkerRunner(handle_sigint=False)
        await runner.add_workers(worker)

        async def guion():
            await asyncio.sleep(0.8)
            await worker.queue_frames([TTSSpeakFrame(_FRASE)])
            await asyncio.sleep(22)
            await worker.queue_frames([EndFrame()])

        await asyncio.gather(runner.run(), guion())

    try:
        asyncio.run(correr())
    except BaseException:
        # El worker cancela al terminar; CancelledError hereda de BaseException.
        pass

    if bufferizada:
        r = getattr(salida, "_reproductor", None)
        if r is None:
            print("    (no se pudo leer el reproductor)")
        else:
            print(f"    callbacks: {r.callbacks}  ·  "
                  f"underflows de PortAudio: {r.underflows_portaudio}  ·  "
                  f"cortes a media frase: {r.underruns}")
    else:
        print(f"    writes: {cuenta['writes']}  ·  "
              f"underflows de PortAudio: {cuenta['underflows']}")


def _diagnostico() -> int:
    """Reproduce la frase por las dos rutas, cada una en su proceso, y compara."""
    import subprocess
    import sys

    print("Se va a oír la misma frase dos veces. Escucha si la primera sale a saltos.\n", flush=True)
    for etiqueta, bandera in (
        ("1/2 · ruta ORIGINAL de Pipecat (write bloqueante, trozos de 40 ms)", "original"),
        ("2/2 · ruta BUFFERIZADA (ring buffer + callback)", "bufferizada"),
    ):
        print(etiqueta, flush=True)
        subprocess.run([sys.executable, __file__, "--" + bandera], check=False)
        print(flush=True)
    print("Si la primera se oyó a saltos y la segunda no, el culpable era el buffer.")
    return 0


if __name__ == "__main__":
    import sys

    if "--original" in sys.argv:
        _reproducir_una_vez(bufferizada=False)
    elif "--bufferizada" in sys.argv:
        _reproducir_una_vez(bufferizada=True)
    else:
        raise SystemExit(_diagnostico())
