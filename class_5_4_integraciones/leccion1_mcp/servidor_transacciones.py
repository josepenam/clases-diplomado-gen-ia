"""Servidor MCP de transacciones de un centro de esquí (mock).

Simula el sistema de ventas de Valle Nevado y expone las tres piezas de MCP:
- Tools:     `crear_pedido` y `aplicar_descuento`, con entrada/salida tipadas (Pydantic).
- Resource:  `resort://catalogo` — el catálogo de productos con precios en CLP.
- Prompt:    `asistente_compra` — una plantilla de interacción parametrizada.

Es un mock: no persiste nada ni consulta APIs reales. El puerto se controla con
la variable de entorno MCP_PORT_TRANSACCIONES (por defecto 8801).
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "TransaccionesValleNevado",
    instructions="Gestiona compras y consultas de productos en Valle Nevado (Chile).",
    port=int(os.environ.get("MCP_PORT_TRANSACCIONES", "8801")),
)


# -------------------------------
# Modelos Pydantic (salida estructurada)
# -------------------------------


class ItemCarrito(BaseModel):
    sku: Literal["forfait", "alquiler", "clase"]
    cantidad: int
    precio_clp: float


class Pedido(BaseModel):
    pedido_id: str
    creado_en: str
    items: list[ItemCarrito]
    total_clp: float
    estado: Literal["pendiente", "confirmado", "cancelado"]


# Con `from __future__ import annotations`, Pydantic v2 necesita reconstruir los
# modelos para resolver las anotaciones diferidas antes de generar los esquemas MCP.
ItemCarrito.model_rebuild()
Pedido.model_rebuild()


# -------------------------------
# Resources
# -------------------------------


@mcp.resource(
    "resort://catalogo",
    title="Catálogo Valle Nevado",
    description="SKUs disponibles y precios en CLP",
    mime_type="application/json",
)
def catalogo() -> dict:
    return {
        "items": [
            {"sku": "forfait", "precio_clp": 65000.0},
            {"sku": "alquiler", "precio_clp": 25000.0},
            {"sku": "clase", "precio_clp": 40000.0},
        ]
    }


# -------------------------------
# Tools
# -------------------------------


@mcp.tool(title="Crear pedido", description="Crea un pedido y devuelve el detalle")
def crear_pedido(items: list[ItemCarrito]) -> Pedido:
    ahora = datetime.now(timezone.utc)
    if not items:
        return Pedido(
            pedido_id="",
            creado_en=ahora.isoformat(),
            items=[],
            total_clp=0.0,
            estado="cancelado",
        )

    total = sum(i.cantidad * i.precio_clp for i in items)
    return Pedido(
        pedido_id="PED-" + ahora.strftime("%Y%m%d%H%M%S"),
        creado_en=ahora.isoformat(),
        items=items,
        total_clp=round(total, 2),
        estado="confirmado",
    )


@mcp.tool(
    title="Aplicar descuento",
    description="Aplica un descuento porcentual a un total en CLP",
)
def aplicar_descuento(total_clp: float, porcentaje: float = 10.0) -> dict:
    porcentaje = max(0.0, min(porcentaje, 100.0))
    con_descuento = total_clp * (1.0 - porcentaje / 100.0)
    return {"total_clp": round(con_descuento, 2), "porcentaje": porcentaje}


# -------------------------------
# Prompts
# -------------------------------


@mcp.prompt(
    title="Asistente de compra (Valle Nevado)",
    description="Ayuda al usuario a armar un carrito respetando un presupuesto en CLP",
)
def asistente_compra(presupuesto_clp: float) -> list[dict]:
    return [
        {
            "role": "user",
            "content": (
                "Quiero armar un carrito en Valle Nevado (Chile) con forfait, alquiler y/o clases "
                f"respetando un presupuesto de {presupuesto_clp} CLP. "
                "Sugiere combinaciones y justifícalas considerando temporada y demanda. "
                "Puedes ofrecer descuentos, y también detallar el clima y el riesgo de aludes."
            ),
        }
    ]


if __name__ == "__main__":
    # streamable-http es el transporte para clientes remotos; para stdio, ver el
    # bloque comentado al final del notebook de la lección.
    print("Iniciando servidor MCP TransaccionesValleNevado…")
    mcp.run(transport="streamable-http")
