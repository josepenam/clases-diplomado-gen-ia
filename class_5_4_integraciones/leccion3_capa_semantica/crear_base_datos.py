"""Crea la base de datos mock del centro de esquí: outputs/montania.db (SQLite).

Simula el sistema operacional "heredado" de un centro de esquí chileno durante
una temporada de invierno (junio–agosto 2026). El desorden es deliberado y
realista:

- Nombres crípticos y abreviados (`trx_pos`, `mnt`, `cod_ln`), sin documentación.
- Solo DOS foreign keys declaradas en el esquema; el resto de los joins son
  convenciones de nombre que solo la gente del equipo conoce.
- Las ventas de punto de venta (`trx_pos.mnt`) están en CLP, pero las reservas
  de agencias internacionales (`res_agt.imp`) están en USD — y NADA en el
  esquema lo dice: la moneda es conocimiento tribal. Esa es la trampa.

Determinística: semilla fija, así el grafo y los resultados son reproducibles.
"""

from __future__ import annotations

import random
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

SEMILLA = 54
RUTA_DB = Path(__file__).resolve().parent / "outputs" / "montania.db"

INICIO_TEMPORADA = date(2026, 6, 1)
DIAS_TEMPORADA = 92  # junio, julio, agosto

ESQUEMA = """
-- catálogo ---------------------------------------------------------------
CREATE TABLE lin_prod (
    linea_id INTEGER PRIMARY KEY,
    cod_ln   TEXT NOT NULL,          -- FORF / ALQ / CLASE / GASTR
    nom      TEXT NOT NULL
);

CREATE TABLE cat_sku (
    sku_id      INTEGER PRIMARY KEY,
    cod         TEXT NOT NULL,
    dsc         TEXT NOT NULL,
    linea_id    INTEGER NOT NULL REFERENCES lin_prod(linea_id),  -- FK declarada
    prc_lst     REAL NOT NULL
);

CREATE TABLE can_venta (
    canal_id INTEGER PRIMARY KEY,
    cod_cn   TEXT NOT NULL,          -- WEB / TAQ / HOTEL / APP
    nom      TEXT NOT NULL
);

-- clientes ---------------------------------------------------------------
CREATE TABLE cli (
    cli_id  INTEGER PRIMARY KEY,
    tp_doc  TEXT NOT NULL,           -- RUT / PAS
    num_doc TEXT NOT NULL,
    nac     TEXT NOT NULL,           -- CL / AR / BR / US / OTRO
    f_alta  TEXT NOT NULL
);

-- ventas -----------------------------------------------------------------
CREATE TABLE trx_pos (
    trx_id   INTEGER PRIMARY KEY,
    ts       TEXT NOT NULL,
    sku_id   INTEGER NOT NULL REFERENCES cat_sku(sku_id),        -- FK declarada
    canal_id INTEGER NOT NULL,       -- join por convención → can_venta
    cli_id   INTEGER NOT NULL,       -- join por convención → cli
    cant     INTEGER NOT NULL,
    mnt      REAL NOT NULL              -- monto... ¿en qué moneda? el esquema no lo dice
);

-- reservas de agencias (¡en USD!) -----------------------------------------
CREATE TABLE agt_ext (
    agt_id INTEGER PRIMARY KEY,
    nom    TEXT NOT NULL,
    pais   TEXT NOT NULL
);

CREATE TABLE res_agt (
    res_id  INTEGER PRIMARY KEY,
    f_res   TEXT NOT NULL,
    agt_id  INTEGER NOT NULL,        -- join por convención → agt_ext
    pax     INTEGER NOT NULL,
    imp     REAL NOT NULL             -- 'importe'... en USD, pero eso no está escrito en ninguna parte
);

-- montaña ----------------------------------------------------------------
CREATE TABLE sec_mont (
    sector_id INTEGER PRIMARY KEY,
    cod       TEXT NOT NULL,
    nom       TEXT NOT NULL,
    cota_m    INTEGER NOT NULL,
    dif       TEXT NOT NULL          -- verde / azul / roja / negra
);

CREATE TABLE med_nieve (
    med_id    INTEGER PRIMARY KEY,
    f         TEXT NOT NULL,
    sector_id INTEGER NOT NULL,      -- join por convención → sec_mont
    base_cm   REAL NOT NULL,
    n24_cm    REAL NOT NULL,
    tmin_c    REAL NOT NULL
);

CREATE TABLE acc_lift (
    acc_id    INTEGER PRIMARY KEY,
    ts        TEXT NOT NULL,
    sector_id INTEGER NOT NULL,      -- join por convención → sec_mont
    cli_id    INTEGER NOT NULL       -- join por convención → cli
);

-- tipo de cambio de referencia --------------------------------------------
CREATE TABLE fx_ref (
    f       TEXT PRIMARY KEY,
    usd_clp REAL NOT NULL
);
"""

LINEAS = [
    (1, "FORF", "Forfaits (tickets de andarivel)"),
    (2, "ALQ", "Alquiler de equipos"),
    (3, "CLASE", "Clases de esquí y snowboard"),
    (4, "GASTR", "Gastronomía"),
]

SKUS = [
    # (cod, dsc, linea_id, precio CLP)
    ("FORF-AD", "Forfait adulto día completo", 1, 65000),
    ("FORF-NI", "Forfait niño día completo", 1, 45000),
    ("FORF-MD", "Forfait medio día", 1, 42000),
    ("ALQ-SKI", "Alquiler equipo ski completo", 2, 25000),
    ("ALQ-SNB", "Alquiler equipo snowboard", 2, 27000),
    ("ALQ-CAS", "Alquiler casco", 2, 6000),
    ("CLS-GRP", "Clase grupal 2 horas", 3, 40000),
    ("CLS-PRV", "Clase privada 1 hora", 3, 75000),
    ("GAS-ALM", "Almuerzo montaña", 4, 18000),
    ("GAS-CAF", "Café + kuchen", 4, 7500),
]

CANALES = [
    (1, "WEB", "Venta web"),
    (2, "TAQ", "Taquilla presencial"),
    (3, "HOTEL", "Convenio hoteles"),
    (4, "APP", "App móvil"),
]

SECTORES = [
    (1, "PLZ", "La Plaza", 2860, "verde"),
    (2, "AND", "El Andino", 3100, "azul"),
    (3, "TRE", "Tres Puntas", 3320, "roja"),
    (4, "BNG", "Barros Negros", 3670, "negra"),
]

AGENCIAS = [
    (1, "Andes Ski Tours", "BR"),
    (2, "Powder South", "US"),
    (3, "Nieve Argentina Viajes", "AR"),
    (4, "SkiChile Operator", "CL"),
]

NACIONALIDADES = ["CL"] * 6 + ["AR"] * 2 + ["BR"] * 2 + ["US", "OTRO"]


def crear(ruta: Path = RUTA_DB, verboso: bool = True) -> Path:
    rng = random.Random(SEMILLA)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.unlink(missing_ok=True)

    con = sqlite3.connect(ruta)
    con.executescript(ESQUEMA)

    con.executemany("INSERT INTO lin_prod VALUES (?,?,?)", LINEAS)
    con.executemany(
        "INSERT INTO cat_sku (cod, dsc, linea_id, prc_lst) VALUES (?,?,?,?)", SKUS
    )
    con.executemany("INSERT INTO can_venta VALUES (?,?,?)", CANALES)
    con.executemany("INSERT INTO sec_mont VALUES (?,?,?,?,?)", SECTORES)
    con.executemany("INSERT INTO agt_ext VALUES (?,?,?)", AGENCIAS)

    # clientes
    clientes = []
    for cli_id in range(1, 801):
        nac = rng.choice(NACIONALIDADES)
        tp_doc = "RUT" if nac == "CL" else "PAS"
        alta = INICIO_TEMPORADA - timedelta(days=rng.randint(0, 900))
        clientes.append((cli_id, tp_doc, f"{rng.randint(5_000_000, 26_999_999)}-{rng.randint(0,9)}", nac, alta.isoformat()))
    con.executemany("INSERT INTO cli VALUES (?,?,?,?,?)", clientes)

    # tipo de cambio: camina alrededor de 940 CLP/USD
    fx, valor = [], 940.0
    for d in range(DIAS_TEMPORADA):
        valor = max(880.0, min(1000.0, valor + rng.uniform(-6, 6)))
        fx.append(((INICIO_TEMPORADA + timedelta(days=d)).isoformat(), round(valor, 2)))
    con.executemany("INSERT INTO fx_ref VALUES (?,?)", fx)

    # nieve por día y sector: base que crece hacia julio y decae en agosto
    mediciones, med_id = [], 1
    for d in range(DIAS_TEMPORADA):
        fecha = INICIO_TEMPORADA + timedelta(days=d)
        estacionalidad = 1.0 - abs(d - 45) / 60.0  # pico a mitad de temporada
        for sector_id, _, _, cota, _ in SECTORES:
            base = max(20.0, 180.0 * estacionalidad + (cota - 2800) / 12 + rng.uniform(-15, 15))
            n24 = max(0.0, rng.gauss(4.0 + 8.0 * estacionalidad, 6.0))
            tmin = round(rng.gauss(-7.0 - (cota - 2800) / 400, 2.5), 1)
            mediciones.append((med_id, fecha.isoformat(), sector_id, round(base, 1), round(n24, 1), tmin))
            med_id += 1
    con.executemany("INSERT INTO med_nieve VALUES (?,?,?,?,?,?)", mediciones)

    # nieve promedio del día (para correlacionar ventas con nieve)
    nieve_dia = {}
    for _, f, _, _, n24, _ in mediciones:
        nieve_dia.setdefault(f, []).append(n24)
    nieve_dia = {f: sum(v) / len(v) for f, v in nieve_dia.items()}

    # ventas POS: más ventas los fines de semana y cuando nieva
    transacciones, trx_id = [], 1
    precios = {i + 1: SKUS[i][3] for i in range(len(SKUS))}
    for d in range(DIAS_TEMPORADA):
        fecha = INICIO_TEMPORADA + timedelta(days=d)
        finde = fecha.weekday() >= 5
        base_dia = 40 + (25 if finde else 0) + int(nieve_dia[fecha.isoformat()] * 1.5)
        for _ in range(max(10, int(rng.gauss(base_dia, 8)))):
            sku_id = rng.randint(1, len(SKUS))
            cant = rng.choice([1, 1, 1, 2, 2, 3, 4])
            hora = rng.randint(8, 16)
            ts = datetime(fecha.year, fecha.month, fecha.day, hora, rng.randint(0, 59))
            transacciones.append((
                trx_id, ts.isoformat(sep=" "), sku_id,
                rng.choice([1, 1, 2, 2, 2, 3, 4]),   # canal
                rng.randint(1, 800),                  # cliente
                cant, cant * precios[sku_id],
            ))
            trx_id += 1
    con.executemany("INSERT INTO trx_pos VALUES (?,?,?,?,?,?,?)", transacciones)

    # reservas de agencias, EN USD: paquetes de varios días por persona
    reservas = []
    for res_id in range(1, 401):
        f_res = INICIO_TEMPORADA + timedelta(days=rng.randint(0, DIAS_TEMPORADA - 1))
        pax = rng.choice([2, 2, 4, 4, 6, 8, 10, 15])
        reservas.append((res_id, f_res.isoformat(), rng.randint(1, 4), pax, round(pax * rng.uniform(180, 420), 2)))
    con.executemany("INSERT INTO res_agt VALUES (?,?,?,?,?)", reservas)

    # pasadas de torniquete
    accesos, acc_id = [], 1
    for d in range(DIAS_TEMPORADA):
        fecha = INICIO_TEMPORADA + timedelta(days=d)
        finde = fecha.weekday() >= 5
        for _ in range(max(20, int(rng.gauss(70 + (40 if finde else 0), 15)))):
            hora = rng.randint(9, 16)
            ts = datetime(fecha.year, fecha.month, fecha.day, hora, rng.randint(0, 59))
            accesos.append((acc_id, ts.isoformat(sep=" "), rng.choice([1, 1, 2, 2, 2, 3, 3, 4]), rng.randint(1, 800)))
            acc_id += 1
    con.executemany("INSERT INTO acc_lift VALUES (?,?,?,?)", accesos)

    con.commit()

    if verboso:
        tablas = [r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )]
        print(f"✓ {ruta.name} creada con {len(tablas)} tablas:")
        for t in tablas:
            n = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            print(f"  {t:<10} {n:>6} filas")
    con.close()
    return ruta


if __name__ == "__main__":
    crear()
