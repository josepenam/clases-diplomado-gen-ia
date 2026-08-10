"""Genera los CSVs de metadata para el conector CSV de neocarta.

Introspecta la base SQLite (PRAGMA table_info / foreign_key_list) y escribe en
outputs/metadata_csv/ los archivos que neocarta ingiere para construir la capa
TÉCNICA del grafo:

  database_info.csv, schema_info.csv, table_info.csv, column_info.csv
  column_references_info.csv   ← solo las FKs REALMENTE declaradas en SQLite
  value_info.csv               ← valores de columnas tipo catálogo (pocos valores)
  glossary_info.csv, category_info.csv, business_term_info.csv  ← del glosario

Nota pedagógica: la capa técnica NO lleva descripciones de negocio ni los joins
por convención — eso es exactamente lo que el esquema no sabe de sí mismo, y
llega después con la ontología (construir_capa_negocio.py).
"""

from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

import yaml

AQUI = Path(__file__).resolve().parent
RUTA_DB = AQUI / "outputs" / "montania.db"
DIR_CSV = AQUI / "outputs" / "metadata_csv"

BASE = "montania"
ESQUEMA = "main"

# columnas catálogo: pocas categorías → sus valores le sirven al grafo
MAX_VALORES_DISTINTOS = 12


def escribir(nombre: str, encabezado: list[str], filas: list[list]) -> None:
    with open(DIR_CSV / nombre, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(encabezado)
        w.writerows(filas)
    print(f"  {nombre:<28} {len(filas):>4} filas")


def generar(verboso: bool = True) -> Path:
    DIR_CSV.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(RUTA_DB)

    tablas = [
        r[0]
        for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
    ]

    escribir("database_info.csv", ["database_name", "service", "platform"], [[BASE, "SQLITE", "LOCAL"]])
    escribir("schema_info.csv", ["database_name", "schema_name"], [[BASE, ESQUEMA]])
    escribir("table_info.csv", ["database_name", "schema_name", "table_name"], [[BASE, ESQUEMA, t] for t in tablas])

    columnas, referencias, valores = [], [], []
    for tabla in tablas:
        fks = {r[3]: (r[2], r[4]) for r in con.execute(f"PRAGMA foreign_key_list({tabla})")}
        # r = (id, seq, tabla_destino, col_origen, col_destino, ...)
        for _, nombre, tipo, _notnull, _dflt, es_pk in con.execute(f"PRAGMA table_info({tabla})"):
            columnas.append([BASE, ESQUEMA, tabla, nombre, tipo or "TEXT",
                             "true" if es_pk else "false",
                             "true" if nombre in fks else "false"])
            if nombre in fks:
                destino_tabla, destino_col = fks[nombre]
                referencias.append([BASE, ESQUEMA, tabla, nombre, BASE, ESQUEMA, destino_tabla, destino_col,
                                    f"{tabla}.{nombre} = {destino_tabla}.{destino_col}"])
            # valores de columnas catálogo (texto con pocas categorías)
            if (tipo or "").upper() == "TEXT":
                distintos = con.execute(
                    f"SELECT DISTINCT {nombre} FROM {tabla} LIMIT {MAX_VALORES_DISTINTOS + 1}"
                ).fetchall()
                if 0 < len(distintos) <= MAX_VALORES_DISTINTOS and nombre not in ("f", "ts", "f_res", "f_alta", "num_doc"):
                    valores.extend([BASE, ESQUEMA, tabla, nombre, v[0]] for v in distintos)

    escribir(
        "column_info.csv",
        ["database_name", "schema_name", "table_name", "column_name", "data_type", "is_primary_key", "is_foreign_key"],
        columnas,
    )
    escribir(
        "column_references_info.csv",
        ["source_database_name", "source_schema_name", "source_table_name", "source_column_name",
         "target_database_name", "target_schema_name", "target_table_name", "target_column_name", "criteria"],
        referencias,
    )
    escribir("value_info.csv", ["database_name", "schema_name", "table_name", "column_name", "value"], valores)

    # glosario de negocio, desde la ontología
    ontologia = yaml.safe_load((AQUI / "ontologia.yaml").read_text())
    glosario = ontologia["glosario"]
    escribir("glossary_info.csv", ["glossary_name", "description"], [[glosario["nombre"], glosario["descripcion"]]])
    categorias, terminos = [], []
    for cat, cuerpo in glosario["categorias"].items():
        categorias.append([glosario["nombre"], cat, cuerpo["descripcion"]])
        terminos.extend(
            [glosario["nombre"], cat, termino, descripcion]
            for termino, descripcion in cuerpo["terminos"].items()
        )
    escribir("category_info.csv", ["glossary_name", "category_name", "description"], categorias)
    escribir("business_term_info.csv", ["glossary_name", "category_name", "term_name", "description"], terminos)

    con.close()
    if verboso:
        print(f"✓ metadata en {DIR_CSV.relative_to(AQUI)}")
    return DIR_CSV


if __name__ == "__main__":
    generar()
