"""Genera los 4 diagramas de la lección 4: la estructura de operación de cada framework.

Para regenerarlos (desde la carpeta de la lección):

    uv run --with matplotlib python diagramas/generar_diagramas.py

Lenguaje visual común para que sean comparables:
- Zona azul   = TU PROCESO (lo que corre en tu máquina y mantienes tú)
- Zona ámbar  = LA NUBE (lo que corre donde el proveedor)
- Flechas verdes  = camino del audio
- Flechas grises  = eventos / control
- Flechas naranjas = herramientas (function calling)
- Banda inferior  = tips de implementación medidos en la clase

El tamaño relativo de las dos zonas ES el mensaje: dónde vive la lógica.
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from pathlib import Path

SALIDA = Path(__file__).resolve().parent
SALIDA.mkdir(exist_ok=True)

# Paleta
AZUL_F, AZUL_B = "#eaf2fd", "#1d4ed8"      # tu proceso
AMBAR_F, AMBAR_B = "#fdf3e3", "#b45309"    # la nube
VERDE = "#15803d"                            # audio
GRIS = "#64748b"                             # eventos / control
NARANJA = "#ea580c"                          # herramientas
TINTA = "#1e293b"
TIPS_F, TIPS_B = "#fefce8", "#a16207"

plt.rcParams["font.family"] = "DejaVu Sans"


def lienzo(titulo, subtitulo, badge):
    fig, ax = plt.subplots(figsize=(16, 10), dpi=115)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    ax.text(2.5, 96.8, titulo, fontsize=23, fontweight="bold", color=TINTA, va="center")
    ax.text(2.5, 92.6, subtitulo, fontsize=12.5, color=GRIS, va="center")
    ax.add_patch(FancyBboxPatch((70, 92.6), 27.5, 6.2, boxstyle="round,pad=0.4",
                                fc="#f1f5f9", ec=GRIS, lw=1.2))
    ax.text(83.75, 95.7, badge, fontsize=10.5, ha="center", va="center", color=TINTA)
    ax.text(2.5, 89.3, "el mismo agente en los cuatro: Luis, Ferretería Central — tienda.py",
            fontsize=9.5, color=GRIS, style="italic")
    return fig, ax


def zona(ax, x, y, w, h, etiqueta, fc, ec):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.5",
                                fc=fc, ec=ec, lw=1.8))
    ax.text(x + 1.4, y + h - 1.4, etiqueta, fontsize=11.5, fontweight="bold",
            color=ec, va="top", linespacing=1.35)


def caja(ax, cx, cy, w, h, texto, fc="white", ec=TINTA, fs=10, lw=1.3, peso="normal"):
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                                boxstyle="round,pad=0.35", fc=fc, ec=ec, lw=lw))
    ax.text(cx, cy, texto, ha="center", va="center", fontsize=fs,
            color=TINTA, fontweight=peso, linespacing=1.45)


def flecha(ax, p1, p2, color=GRIS, lw=2.2, texto=None, fs=9.5, dxy=(0, 1.6),
           rad=0.0, estilo="-"):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=17,
                                 color=color, lw=lw, linestyle=estilo,
                                 connectionstyle=f"arc3,rad={rad}", zorder=5))
    if texto:
        mx, my = (p1[0] + p2[0]) / 2 + dxy[0], (p1[1] + p2[1]) / 2 + dxy[1]
        ax.text(mx, my, texto, fontsize=fs, color=color, ha="center",
                fontweight="bold", zorder=6, linespacing=1.3)


def tips(ax, items):
    ax.add_patch(FancyBboxPatch((1.5, 1.2), 97, 13.6, boxstyle="round,pad=0.4",
                                fc=TIPS_F, ec=TIPS_B, lw=1.5))
    ax.text(3.2, 12.6, "Tips de implementación (medidos en la clase)",
            fontsize=11, fontweight="bold", color=TIPS_B)
    y = 9.9
    for item in items:
        ax.text(3.6, y, "•  " + item, fontsize=10, color=TINTA, va="center")
        y -= 2.65


# ═══════════════════════════════════════════════════════════════════════
# 0 · Nivel 0 — WebSocket crudo
# ═══════════════════════════════════════════════════════════════════════

def d0():
    fig, ax = lienzo(
        "Nivel 0 · la API Realtime a pelo",
        "nivel0_websocket_crudo.py — sin framework: el protocolo de cable, a mano",
        "vocabulario: 56 eventos\n(11 envías · 45 recibes)",
    )
    zona(ax, 2, 17, 53, 70.5, "TU PROCESO — todo lo escribes tú", AZUL_F, AZUL_B)
    zona(ax, 59, 17, 39, 70.5, "NUBE OPENAI", AMBAR_F, AMBAR_B)

    caja(ax, 12, 77, 15, 8, "Micrófono\nPyAudio · PCM16")
    caja(ax, 36.5, 77, 24, 8, "base64 →\ninput_audio_buffer.append")
    caja(ax, 27, 56.5, 41, 13,
         "Bucle de eventos — interpretas JSON a mano\n"
         "response.output_audio.delta → decodificar base64\n"
         "speech_started → interrumpir y truncate",
         fs=9.8)
    caja(ax, 31.5, 38, 33, 12,
         "consultar_stock() y responder\nen DOS mensajes:\n"
         "① conversation.item.create   ② response.create",
         ec=NARANJA, fs=9.6)
    caja(ax, 13.5, 23.5, 19, 7.5, "ReproductorFluido\n(jitter buffer)", ec=VERDE)
    caja(ax, 40, 23.5, 13, 7, "Parlante", ec=VERDE)
    ax.text(31.5, 30.2, "⚠ sin ② el agente queda mudo, sin error",
            fontsize=8.8, color=NARANJA, ha="center", style="italic")

    caja(ax, 78.5, 77, 33, 8, "WebSocket  wss://…/v1/realtime")
    caja(ax, 78.5, 52, 34, 17,
         "gpt-realtime-2.1\n"
         "oye y habla directamente (sin STT/TTS)\n"
         "semantic_vad: decide los turnos\n"
         "interrupt_response: se corta al oírte",
         fs=10)

    flecha(ax, (19.5, 77), (24.5, 77), VERDE)
    flecha(ax, (48.5, 77), (62, 77), VERDE, texto="audio ↑", dxy=(0, 1.8))
    flecha(ax, (78.5, 73), (78.5, 60.7), GRIS)
    flecha(ax, (61.5, 49), (47.7, 57), GRIS, texto="eventos JSON ↓\n(45 tipos)",
           dxy=(6.3, -6.8), rad=0.15)
    flecha(ax, (31.5, 50), (31.5, 44.2), NARANJA)
    flecha(ax, (48.2, 40), (63, 73.5), NARANJA, texto="① + ②", dxy=(-5.6, 3.2),
           rad=-0.3)
    flecha(ax, (9, 50), (12.5, 27.5), VERDE, texto="PCM16", dxy=(-3.9, 0))
    flecha(ax, (23.2, 23.5), (33.3, 23.5), VERDE)

    tips(ax, [
        "La forma del session cambió: hoy todo va anidado bajo audio.input / audio.output — un ejemplo de 2024 no corre tal cual.",
        "Tras una herramienta van DOS mensajes; olvidar el response.create deja al agente mudo, sin ningún error.",
        "Si el usuario interrumpe, reconcilias tú: conversation.item.truncate con los milisegundos realmente reproducidos.",
        "Nunca escribas los deltas directo al parlante: llegan a ráfagas (huecos de hasta 1,3 s) → ReproductorFluido.",
    ])
    fig.savefig(SALIDA / "diagrama_0_websocket_crudo.png", bbox_inches="tight",
                facecolor="white")
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════
# 1 · OpenAI Agents SDK
# ═══════════════════════════════════════════════════════════════════════

def d1():
    fig, ax = lienzo(
        "OpenAI Agents SDK · el cliente semántico",
        "agente_openai.py — cerrado: los mismos primitivos que tus agentes de texto",
        "vocabulario: 15 eventos\n(absorbe 41 de los 56 del cable)",
    )
    zona(ax, 2, 17, 53, 70.5, "TU PROCESO", AZUL_F, AZUL_B)
    zona(ax, 59, 17, 39, 70.5, "NUBE OPENAI", AMBAR_F, AMBAR_B)

    caja(ax, 29, 77.5, 38, 9,
         "RealtimeAgent('Luis', instructions, tools)\n"
         "los primitivos de agentes:\ntools · handoffs · guardrails", fs=9.8)
    caja(ax, 29, 61, 38, 11,
         "RealtimeRunner  →  session\n"
         "session.send_audio(bytes)\n"
         "async for evento in session  (15 eventos)",
         fs=9.8)
    caja(ax, 24, 41, 18, 8.5, "@function_tool\nconsultar_stock()", ec=NARANJA, fs=9.6)
    caja(ax, 42.5, 41, 16, 8.5, "audio_interrupted\n→ interrupt()", ec=GRIS, fs=9.6)
    caja(ax, 12, 24, 14, 7.5, "Micrófono\nPyAudio", ec=VERDE)
    caja(ax, 33, 24, 19, 7.5, "ReproductorFluido\n(jitter buffer)", ec=VERDE)
    caja(ax, 49.5, 24, 9.5, 7, "Parlante", ec=VERDE)

    caja(ax, 78.5, 70, 33, 10,
         "gpt-realtime-2.1\nsemantic_vad — turnos e\ninterrupciones en el servidor")
    caja(ax, 78.5, 47, 33, 12,
         "El SDK habla el protocolo\ncompleto por ti\n(los 56 eventos, ocultos)\n"
         "raw_model_event = escotilla", fs=9.8)

    flecha(ax, (29, 72.7), (29, 66.9), GRIS)
    flecha(ax, (48.3, 63), (62, 68.5), GRIS, texto="WebSocket\n(protocolo oculto)",
           dxy=(1, 3.6), rad=-0.12)
    flecha(ax, (24, 55.2), (24, 45.6), NARANJA,
           texto="tool_start /\ntool_end", dxy=(-17.2, 0.3), fs=8.8)
    flecha(ax, (42.5, 55.2), (42.5, 45.6), GRIS)
    flecha(ax, (12, 27.9), (13, 55.2), VERDE, texto="send_audio()", dxy=(-5, 0), fs=8.8)
    flecha(ax, (33, 55.2), (33, 28.1), VERDE, texto="evento «audio»", dxy=(10, -11),
           fs=8.8)
    flecha(ax, (41, 36.6), (35.5, 28.1), GRIS, lw=1.6)
    flecha(ax, (42.8, 24), (44.5, 24), VERDE)

    tips(ax, [
        "56 eventos de cable → 15 con significado; el ida y vuelta de la herramienta (incluido el response.create) lo hace el SDK.",
        "La plomería de audio NO viene: micrófono y parlante los cableas tú con PyAudio — es la mitad del script.",
        "semantic_vad decide el turno por el contenido, no por el silencio: aguanta un «quiero… un… taladro» sin cortarte.",
        "Cuando la abstracción no alcanza, raw_model_event te da el evento crudo sin abandonar el framework.",
    ])
    fig.savefig(SALIDA / "diagrama_1_openai_agents_sdk.png", bbox_inches="tight",
                facecolor="white")
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════
# 2 · Pipecat
# ═══════════════════════════════════════════════════════════════════════

def d2():
    fig, ax = lienzo(
        "Pipecat · el bus de frames",
        "agente_pipecat.py — open source (Daily): la conversación es un pipeline de procesadores",
        "vocabulario: ~130 frames\nSystem · Data · Control",
    )
    zona(ax, 2, 17, 76, 70.5, "TU PROCESO — el pipeline completo vive acá", AZUL_F, AZUL_B)
    zona(ax, 81, 17, 17, 70.5, "NUBE", AMBAR_F, AMBAR_B)

    y = 68
    caja(ax, 12, y, 16, 12, "transport\n.input()\n+ VAD Silero\n(local)", fs=9.3)
    caja(ax, 30, y, 15, 10, "user_\naggregator\n(contexto)", fs=9.3)
    caja(ax, 49, y, 18, 12, "OpenAIRealtime\nLLMService\n(voice-to-voice)", fs=9.3)
    caja(ax, 68.5, y, 15, 12, "SalidaLocal\nFluida\n(jitter buffer)", fs=9.3, ec=VERDE)

    flecha(ax, (20.2, y), (22.3, y), VERDE)
    ax.text(21.2, 59.6, "InputAudio\nRawFrame", fontsize=8.4, color=VERDE,
            ha="center", fontweight="bold")
    flecha(ax, (37.7, y), (39.8, y), GRIS)
    ax.text(38.8, 59.6, "LLMContext\nFrame", fontsize=8.4, color=GRIS,
            ha="center", fontweight="bold")
    flecha(ax, (58.2, y), (60.8, y), VERDE)
    ax.text(59.5, 59.6, "OutputAudio\nRawFrame", fontsize=8.4, color=VERDE,
            ha="center", fontweight="bold")
    flecha(ax, (56, 74.2), (89.5, 76.6), AMBAR_B, texto="WS", dxy=(0, 2.2), rad=-0.2)

    caja(ax, 89.5, 71, 14.5, 11, "OpenAI\ngpt-realtime-2.1", fs=9.3)

    caja(ax, 40, 48.5, 70, 8,
         "El bus: los procesadores NO consumen los frames — los pasan. "
         "Tres familias con prioridad distinta:\n"
         "SystemFrame (urgente, se adelanta)  ·  DataFrame (audio/texto)  ·  ControlFrame (inicio/fin)",
         fs=9.6, ec=GRIS)
    caja(ax, 40, 35.5, 70, 8,
         "Interrupción = broadcast_interruption(): un InterruptionFrame viaja ↑ y ↓ a la vez\n"
         "cada etapa se resetea sola — por eso interrumpir funciona sin escribir nada",
         fs=9.6, ec=GRIS)
    caja(ax, 40, 23, 70, 8.5,
         "modo --cascada: la MISMA lista + 2 etapas  →  "
         "input → STT → contexto → LLM → TTS → output\n"
         "(cambiar de arquitectura o de proveedor = editar la lista)",
         fs=9.6, ec=AZUL_B)

    tips(ax, [
        "nltk bloquea imports con el .venv dentro del proyecto (convención de uv) → NLTK_DISABLE_IMPORT_SECURITY=1 antes de importar.",
        "La salida local hace underflow en el 100% de los writes (medido: 310/310) → transporte_local_fluido() con ring buffer: 0.",
        "El VAD (Silero) corre EN TU MÁQUINA: detectar si estás hablando no manda audio a ningún servidor.",
        "Fija las tasas explícitas (24 kHz para la API Realtime): los defaults de PipelineParams son 16 kHz de entrada.",
    ])
    fig.savefig(SALIDA / "diagrama_2_pipecat.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════
# 3 · ElevenLabs Agents
# ═══════════════════════════════════════════════════════════════════════

def d3():
    fig, ax = lienzo(
        "ElevenLabs Agents · la plataforma",
        "agente_elevenlabs.py — el agente NO vive en tu código: es un recurso en la nube",
        "vocabulario: 9 eventos\nsolo 2 te obligan a actuar",
    )
    zona(ax, 2, 17, 34, 70.5, "TU PROCESO — presta el mic\ny ejecuta las herramientas",
         AZUL_F, AZUL_B)
    zona(ax, 40, 17, 58, 70.5, "PLATAFORMA ELEVENLABS — acá vive el agente",
         AMBAR_F, AMBAR_B)

    caja(ax, 19, 71, 28, 10,
         "Conversation\nrequires_auth=True\ncallbacks (transcript, respuesta)", fs=9.6)
    caja(ax, 19, 52.5, 28, 10,
         "InterfazAudioFluida\nmicrófono + parlante\n(jitter buffer)", ec=VERDE, fs=9.6)
    caja(ax, 19, 33, 28, 11,
         "ClientTools\nconsultar_stock() — se ejecuta\nacá, pero se declara ALLÁ →",
         ec=NARANJA, fs=9.6)
    ax.text(19, 24.4, "lo único obligatorio: responder ping→pong\ny ejecutar client_tool_call",
            fontsize=8.8, color=GRIS, ha="center", style="italic")

    caja(ax, 68.5, 71.5, 51, 11,
         "EL AGENTE (recurso creado por API)\n"
         "prompt · LLM gpt-4o-mini · voz · idioma es → eleven_flash_v2_5\n"
         "las herramientas se declaran en su config",
         fs=9.8)
    caja(ax, 58.5, 53.5, 21, 10.5,
         "Turnos, VAD e\ninterrupciones\n+ telefonía incluida", fs=9.6)
    caja(ax, 84, 53.5, 24, 10.5,
         "Panel: conversaciones\ngrabadas y transcritas\n(observabilidad gratis)", fs=9.6)
    caja(ax, 71.5, 34, 45, 10,
         "Si lo interrumpes → agent_response_correction:\n"
         "te llega el texto CORREGIDO\n(lo que alcanzó a decir de verdad)",
         fs=9.6, ec=GRIS)

    flecha(ax, (33.5, 73.8), (43, 74.6), GRIS, texto="WS · 9 eventos", dxy=(0, 2.2),
           fs=9)
    flecha(ax, (43, 70.8), (33.5, 70.2), GRIS)
    flecha(ax, (19, 66), (19, 57.7), VERDE, texto="audio ↑↓", dxy=(6.8, 0))
    flecha(ax, (45, 66), (41, 38.8), NARANJA, lw=1.8, rad=0.05)
    flecha(ax, (41, 36.5), (33.5, 36.5), NARANJA, texto="client_tool_call",
           dxy=(2, 2.1), fs=8.8)
    flecha(ax, (33.5, 30.5), (41, 30.5), NARANJA, texto="client_tool_result",
           dxy=(2, -2.8), fs=8.8)

    tips(ax, [
        "Un agente en ESPAÑOL debe usar eleven_flash_v2_5 o turbo — la API rechaza los demás modelos de TTS.",
        "En plan free solo funcionan voces premade; las de biblioteca (p. ej. acento chileno) devuelven 402 paid_plan_required.",
        "La herramienta se declara en la CONFIG del agente (la plataforma decide cuándo llamarla); tu proceso solo la ejecuta.",
        "El script crea el agente al entrar y lo BORRA al salir; --conservar lo deja para inspeccionarlo en el dashboard.",
    ])
    fig.savefig(SALIDA / "diagrama_3_elevenlabs_agents.png", bbox_inches="tight",
                facecolor="white")
    plt.close(fig)


d0()
d1()
d2()
d3()
for p in sorted(SALIDA.glob("*.png")):
    print(p.name, f"{p.stat().st_size/1024:.0f} KB")
