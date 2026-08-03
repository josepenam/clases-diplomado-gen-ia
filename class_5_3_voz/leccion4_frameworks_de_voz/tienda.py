"""El dominio compartido por los tres frameworks: una tienda con stock.

Los tres agentes de esta lección resuelven exactamente el mismo problema con la misma
herramienta, para que la comparación sea entre *frameworks* y no entre demos distintas.
El caso viene del material original de la clase (`check_product_stock`).
"""

INSTRUCCIONES = """
Te llamas Luis y atiendes por teléfono la tienda "Ferretería Central", en Santiago de Chile.

Cómo hablas:
- Español de Chile, informal y cercano, como una conversación telefónica real.
- Frases cortas. Nunca listas ni enumeraciones: esto es una conversación hablada.
- Si te preguntan por un producto, usa la herramienta consultar_stock antes de responder.
- Si el producto no está en el catálogo, dilo derecho y ofrece alguna alternativa del catálogo.
- Los precios dilos en pesos chilenos, redondeados y como se pronuncian.

Saluda al inicio con una frase breve y pregunta en qué puedes ayudar.
"""

# El "inventario". En un sistema real esto sería una consulta a la base de datos o al ERP.
CATALOGO: dict[str, dict] = {
    "taladro": {"stock": 12, "precio": 54990},
    "martillo": {"stock": 40, "precio": 8990},
    "destornillador": {"stock": 0, "precio": 3490},
    "sierra circular": {"stock": 3, "precio": 89990},
    "cemento": {"stock": 150, "precio": 6290},
    "pintura blanca": {"stock": 7, "precio": 24990},
}


def consultar_stock(nombre_producto: str) -> dict:
    """Busca un producto en el catálogo y devuelve su disponibilidad y precio.

    Es una función normal de Python: los tres frameworks la envuelven de forma distinta,
    pero la lógica de negocio es idéntica en los tres. Ese es justamente el punto.
    """
    consulta = (nombre_producto or "").strip().lower()

    # Búsqueda tolerante: "un taladro", "taladros", "taladro percutor" → "taladro"
    for producto, datos in CATALOGO.items():
        if producto in consulta or consulta in producto:
            return {
                "producto": producto,
                "disponible": datos["stock"] > 0,
                "unidades": datos["stock"],
                "precio_clp": datos["precio"],
            }

    return {
        "producto": nombre_producto,
        "disponible": False,
        "unidades": 0,
        "error": "producto no encontrado en el catálogo",
        "alternativas": list(CATALOGO)[:3],
    }
