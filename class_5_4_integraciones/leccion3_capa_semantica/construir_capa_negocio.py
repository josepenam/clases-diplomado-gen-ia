"""Construye la capa de NEGOCIO del grafo a partir de ontologia.yaml.

Sobre la capa técnica que cargó neocarta (Database→Schema→Table→Column→Value),
agrega lo que el esquema no sabe de sí mismo:

  (:Table)-[:IN_DOMAIN]->(:BusinessDomain)     dominios de negocio
  (:Table)-[:ABOUT]->(:Metric)                  de qué trata cada tabla
  (:Column)-[:MEASURES]->(:Metric)              qué mide cada columna
  (:Column)-[:IN_CURRENCY]->(:Currency)         ¡en qué moneda!
  (:Column)-[:REFERENCES {source:'convencion'}] los joins que las FKs no declaran
  Table.descripcion                             descripción de negocio

Todas las aristas llevan source:'ontologia' (o 'convencion' para joins), así el
script es idempotente: borra sus propias aristas y las reescribe, sin tocar lo
que cargó neocarta ni lo que agregue el enriquecimiento LLM.
"""

from __future__ import annotations

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv
from neo4j import GraphDatabase

AQUI = Path(__file__).resolve().parent

LIMPIEZA = [
    "MATCH ()-[r:IN_DOMAIN|ABOUT|MEASURES|IN_CURRENCY]->() WHERE r.source = 'ontologia' DELETE r",
    "MATCH ()-[r:REFERENCES]->() WHERE r.source = 'convencion' DELETE r",
    # nodos concepto que quedaron huérfanos (sobreviven los que use otra capa)
    "MATCH (n) WHERE (n:BusinessDomain OR n:Metric OR n:Currency) AND NOT (n)--() DELETE n",
]

DOMINIOS = """
UNWIND $filas AS fila
MATCH (t:Table {name: fila.tabla})
SET t.dominio = fila.dominio, t.descripcion = fila.descripcion
MERGE (d:BusinessDomain {name: fila.dominio})
MERGE (t)-[:IN_DOMAIN {source: 'ontologia'}]->(d)
"""

TABLAS_SOBRE = """
UNWIND $filas AS fila
MATCH (t:Table {name: fila.tabla})
MERGE (m:Metric {name: fila.metrica})
MERGE (t)-[:ABOUT {source: 'ontologia'}]->(m)
"""

CONCEPTOS_COLUMNA = """
UNWIND $filas AS fila
MATCH (:Table {name: fila.tabla})-[:HAS_COLUMN]->(c:Column {name: fila.columna})
FOREACH (_ IN CASE WHEN fila.metrica IS NULL THEN [] ELSE [1] END |
  MERGE (m:Metric {name: fila.metrica})
  MERGE (c)-[:MEASURES {source: 'ontologia'}]->(m))
FOREACH (_ IN CASE WHEN fila.moneda IS NULL THEN [] ELSE [1] END |
  MERGE (cur:Currency {code: fila.moneda})
  MERGE (c)-[:IN_CURRENCY {source: 'ontologia'}]->(cur))
"""

JOINS_CONVENCION = """
UNWIND $filas AS fila
MATCH (:Table {name: fila.desde_tabla})-[:HAS_COLUMN]->(c1:Column {name: fila.desde_col})
MATCH (:Table {name: fila.hasta_tabla})-[:HAS_COLUMN]->(c2:Column {name: fila.hasta_col})
MERGE (c1)-[r:REFERENCES {source: 'convencion'}]->(c2)
SET r.criteria = fila.desde_tabla + '.' + fila.desde_col + ' = ' + fila.hasta_tabla + '.' + fila.hasta_col
"""

COLUMNAS = "MATCH (t:Table)-[:HAS_COLUMN]->(c:Column) RETURN t.name AS tabla, c.name AS columna"


def metrica_de(columna: str, ontologia: dict) -> str | None:
    for metrica, patrones in ontologia["metricas"].items():
        if any(p in columna for p in patrones):
            return metrica
    return None


def moneda_de(tabla: str, columna: str, ontologia: dict) -> str | None:
    # la moneda no se puede adivinar del nombre: es una declaración explícita
    for fila in ontologia["monedas"]:
        if fila["tabla"] == tabla and fila["columna"] == columna:
            return fila["moneda"]
    return None


def construir(verboso: bool = True) -> None:
    load_dotenv(AQUI / ".env", override=True)  # el .env de la lección gana sobre variables heredadas
    ontologia = yaml.safe_load((AQUI / "ontologia.yaml").read_text())

    driver = GraphDatabase.driver(
        os.environ.get("NEO4J_URI", "bolt://localhost:7687"),
        auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ.get("NEO4J_PASSWORD", "password")),
    )
    base = os.environ.get("NEO4J_DATABASE", "neo4j")

    with driver.session(database=base) as sesion:
        for consulta in LIMPIEZA:
            sesion.run(consulta).consume()

        filas_dominio = [
            {"tabla": tabla, "dominio": dominio, "descripcion": ontologia["descripciones"].get(tabla, "")}
            for dominio, tablas in ontologia["dominios"].items()
            for tabla in tablas
        ]
        sesion.run(DOMINIOS, filas=filas_dominio).consume()

        sesion.run(
            TABLAS_SOBRE,
            filas=[{"tabla": t, "metrica": m} for t, m in ontologia["tablas_sobre"].items()],
        ).consume()

        filas_columna = []
        for registro in sesion.run(COLUMNAS):
            filas_columna.append(
                {
                    "tabla": registro["tabla"],
                    "columna": registro["columna"],
                    "metrica": metrica_de(registro["columna"], ontologia),
                    "moneda": moneda_de(registro["tabla"], registro["columna"], ontologia),
                }
            )
        sesion.run(CONCEPTOS_COLUMNA, filas=filas_columna).consume()

        sesion.run(JOINS_CONVENCION, filas=ontologia["convenciones_join"]).consume()

        # marcador de la lección: permite a otros scripts reconocer este grafo
        sesion.run(
            "MERGE (m:__clase_5_4__ {id: 'capa-semantica'}) SET m.actualizado = datetime()"
        ).consume()

        if verboso:
            resumen = sesion.run(
                "MATCH ()-[r]->() WHERE r.source IN ['ontologia', 'convencion'] "
                "RETURN type(r) AS tipo, count(*) AS n ORDER BY n DESC"
            ).data()
            print("✓ capa de negocio construida:")
            for fila in resumen:
                print(f"  -[{fila['tipo']}]-  {fila['n']}")

    driver.close()


if __name__ == "__main__":
    construir()
