"""Genera data/ventas_diarias.csv: el dataset mock de la lección (semilla fija).

Una fila por día y canal de venta durante la temporada (jun-ago 2026):
fecha, canal, trx (nº de transacciones), ventas_clp, nieve_cm (caída del día).
Las ventas correlacionan con la nieve a propósito: hay una relación que
la regresión debe encontrar.
"""

from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

SEMILLA = 54
RUTA = Path(__file__).resolve().parent / "data" / "ventas_diarias.csv"

CANALES = {"web": 1.0, "taquilla": 1.4, "hotel": 0.6, "app": 0.8}


def generar() -> Path:
    rng = random.Random(SEMILLA)
    RUTA.parent.mkdir(parents=True, exist_ok=True)

    filas = []
    for d in range(92):
        fecha = date(2026, 6, 1) + timedelta(days=d)
        estacionalidad = 1.0 - abs(d - 45) / 60.0
        nieve = round(max(0.0, rng.gauss(4.0 + 9.0 * estacionalidad, 5.0)), 1)
        finde = 1.35 if fecha.weekday() >= 5 else 1.0
        for canal, peso in CANALES.items():
            base = 55 * peso * finde * (1.0 + 0.06 * nieve)
            trx = max(5, int(rng.gauss(base, 8)))
            ticket = rng.gauss(52_000, 6_000)
            filas.append([fecha.isoformat(), canal, trx, round(trx * ticket), nieve])

    with open(RUTA, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["fecha", "canal", "trx", "ventas_clp", "nieve_cm"])
        w.writerows(filas)
    print(f"✓ {RUTA.name}: {len(filas)} filas")
    return RUTA


if __name__ == "__main__":
    generar()
