"""Reconstruye TODO el mundo de la lección desde cero, en un solo comando.

    uv run python construir_grafo.py

Deja la lección autocontenida: no hace falta haber corrido la lección 3.
Pasos (idempotentes — correrlo dos veces da el mismo grafo):

  1. Crea la base mock outputs/montania.db (semilla fija).
  2. Genera los CSVs de metadata para neocarta.
  3. BORRA el grafo y carga la capa técnica (conector CSV de neocarta).
  4. Construye la capa de negocio desde ontologia.yaml.

Guardia de seguridad: solo borra el grafo si está vacío o si lo construyó esta
clase (marcador :__clase_5_4__). Si encuentra otra cosa, aborta — apunta
NEO4J_URI a un contenedor propio de la lección en vez de compartir uno.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase

import construir_capa_negocio
import crear_base_datos
import generar_metadata_csv

AQUI = Path(__file__).resolve().parent


def construir(verboso: bool = True) -> None:
    load_dotenv(AQUI / ".env")

    driver = GraphDatabase.driver(
        os.environ.get("NEO4J_URI", "bolt://localhost:7687"),
        auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ.get("NEO4J_PASSWORD", "password")),
    )
    base = os.environ.get("NEO4J_DATABASE", "neo4j")

    with driver.session(database=base) as sesion:
        nodos = sesion.run("MATCH (n) RETURN count(n) AS n").single()["n"]
        es_nuestro = sesion.run(
            "OPTIONAL MATCH (m:__clase_5_4__) RETURN m IS NOT NULL AS ok"
        ).single()["ok"]
        if nodos > 0 and not es_nuestro:
            driver.close()
            raise SystemExit(
                f"⛔ El grafo en {os.environ.get('NEO4J_URI')} tiene {nodos} nodos que esta "
                "clase no creó. No lo voy a borrar.\n"
                "   Apunta NEO4J_URI (en .env) a un contenedor dedicado a la lección, p. ej.:\n"
                "   docker run -d --name neo4j-clase54 -p 7474:7474 -p 7687:7687 "
                "-e NEO4J_AUTH=neo4j/password neo4j:5"
            )

        if verboso:
            print("1/4 base de datos mock…")
        crear_base_datos.crear(verboso=False)

        if verboso:
            print("2/4 metadata para neocarta…")
        dir_csv = generar_metadata_csv.generar(verboso=False)

        if verboso:
            print("3/4 grafo: borrar y cargar capa técnica…")
        sesion.run("MATCH (n) DETACH DELETE n").consume()

        from neocarta.connectors.csv import CSVConnector

        CSVConnector(
            csv_directory=str(dir_csv), neo4j_driver=driver, database_name=base
        ).ingest()

    if verboso:
        print("4/4 capa de negocio…")
    construir_capa_negocio.construir(verboso=False)

    if verboso:
        with driver.session(database=base) as sesion:
            nodos = sesion.run(
                "MATCH (n) WHERE NOT n:__neocarta_graph__ AND NOT n:__clase_5_4__ "
                "RETURN count(n) AS n"
            ).single()["n"]
            aristas = sesion.run("MATCH ()-[r]->() RETURN count(r) AS n").single()["n"]
        print(f"✓ mundo reconstruido: {nodos} nodos, {aristas} relaciones")
    driver.close()


if __name__ == "__main__":
    construir()
