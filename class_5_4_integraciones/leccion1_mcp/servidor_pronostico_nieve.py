"""Servidor MCP de pronóstico de nieve (mock).

Expone las tres piezas de MCP más dos capacidades de contexto que el protocolo
define para las tools:
- Tools:     `obtener_pronostico` (con logging y progreso hacia el cliente vía
             `ctx.info` / `ctx.report_progress`) e `indice_riesgo_aludes`.
- Resources: `nieve://estaciones` (estático) y `nieve://condiciones/{estacion}`
             (dinámico, por plantilla de URI — el parámetro va en el path, donde
             una URL tolera espacios y acentos; en la posición de host no).
- Prompt:    `plan_viaje`.

Es un mock: los datos son simulados. El puerto se controla con la variable de
entorno MCP_PORT_PRONOSTICO (por defecto 8802).
"""

from __future__ import annotations

import asyncio
import os
from datetime import date, timedelta
from typing import Literal

from pydantic import BaseModel, Field
from mcp.server.fastmcp import Context, FastMCP

mcp = FastMCP(
    "PronosticoNieve",
    instructions="Pronóstico de nieve y riesgo de aludes para centros de esquí chilenos.",
    port=int(os.environ.get("MCP_PORT_PRONOSTICO", "8802")),
)


# -------------------------------
# Modelos Pydantic (salida estructurada)
# -------------------------------


class PronosticoDia(BaseModel):
    dia: str = Field(description="Fecha en formato ISO")
    nieve_cm: float = Field(description="Nieve esperada (cm)")
    temperatura_c: float = Field(description="Temperatura media (°C)")
    riesgo_aludes: Literal["bajo", "moderado", "alto"]


class Pronostico(BaseModel):
    estacion: str
    unidades: Literal["metric", "imperial"]
    dias: list[PronosticoDia]


# Con `from __future__ import annotations`, Pydantic v2 necesita reconstruir los
# modelos para resolver las anotaciones diferidas antes de generar los esquemas MCP.
PronosticoDia.model_rebuild()
Pronostico.model_rebuild()


# -------------------------------
# Resources
# -------------------------------


@mcp.resource(
    "nieve://estaciones",
    title="Estaciones conocidas",
    description="Listado de centros de esquí de ejemplo",
    mime_type="application/json",
)
def listar_estaciones() -> dict:
    return {
        "estaciones": [
            "Valle Nevado",
            "La Parva",
            "El Colorado",
            "Portillo",
            "Nevados de Chillán",
            "Corralco",
            "Antillanca",
            "Pucón",
        ]
    }


# Recurso dinámico: la URI lleva un parámetro que se resuelve al momento de leer.
@mcp.resource(
    "nieve://condiciones/{estacion}",
    title="Condiciones actuales",
    description="Condiciones simuladas por estación",
    mime_type="application/json",
)
def condiciones_actuales(estacion: str) -> dict:
    from urllib.parse import unquote

    return {
        "estacion": unquote(estacion),
        "condiciones": {
            "base_cm": 120,
            "ultima_nevada_cm": 8,
            "temperatura_c": -4.5,
            "andariveles_abiertos": 18,
        },
    }


# -------------------------------
# Tools
# -------------------------------


@mcp.tool(
    title="Pronóstico de nieve",
    description="Devuelve un pronóstico simulado para N días",
)
async def obtener_pronostico(
    estacion: str,
    num_dias: int = 3,
    unidades: Literal["metric", "imperial"] = "metric",
    ctx: Context = None,
) -> Pronostico:
    # `ctx` lo inyecta FastMCP: por él viajan logs y progreso hacia el cliente,
    # dentro de la misma sesión MCP (no es un print del lado del servidor).
    await ctx.info(f"Generando pronóstico de {num_dias} días para {estacion}")

    temp_base_c = -6.0
    dias: list[PronosticoDia] = []
    for i in range(num_dias):
        d = date.today() + timedelta(days=i + 1)
        nieve = max(0.0, 15.0 - i * 3.5)
        temp_c = temp_base_c + i * 1.2
        riesgo = "moderado" if nieve > 5 else "bajo"
        if nieve > 20:
            riesgo = "alto"
        dias.append(
            PronosticoDia(
                dia=d.isoformat(),
                nieve_cm=nieve,
                temperatura_c=temp_c,
                riesgo_aludes=riesgo,
            )
        )
        await ctx.report_progress(progress=i + 1, total=num_dias)
        await asyncio.sleep(0.05)  # simula trabajo para que el progreso se aprecie

    return Pronostico(estacion=estacion, unidades=unidades, dias=dias)


@mcp.tool(
    title="Índice de riesgo de aludes",
    description="Calcula un índice simple a partir de pendiente, nieve reciente y viento",
)
def indice_riesgo_aludes(
    pendiente_grados: float,
    nieve_reciente_cm: float,
    viento_kmh: float,
) -> dict:
    puntaje = 0.4 * pendiente_grados + 0.3 * nieve_reciente_cm + 0.3 * (viento_kmh / 10.0)
    nivel = "bajo"
    if puntaje > 30:
        nivel = "moderado"
    if puntaje > 50:
        nivel = "alto"
    return {"puntaje": round(puntaje, 2), "nivel": nivel}


# -------------------------------
# Prompts
# -------------------------------


@mcp.prompt(
    title="Plan de viaje de nieve",
    description="Guía para planificar un viaje de esquí",
)
def plan_viaje(estacion: str, dias: int) -> list[dict]:
    return [
        {
            "role": "user",
            "content": (
                f"Quiero planear {dias} días de esquí en {estacion}. "
                "Indica la mejor ventana de tiempo, el material recomendado y los riesgos."
            ),
        }
    ]


if __name__ == "__main__":
    print("Iniciando servidor MCP PronosticoNieve…")
    mcp.run(transport="streamable-http")
