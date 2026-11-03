import sqlite3
from contextlib import closing

DB_PATH = "seguridad.db"
SEVERIDADES = ("Baja", "Media", "Alta", "Critica")

ESQUEMA = """
CREATE TABLE IF NOT EXISTS hallazgos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo INTEGER NOT NULL,
    fecha TEXT NOT NULL,
    categoria TEXT NOT NULL,
    severidad TEXT NOT NULL
        CHECK (severidad IN ('Baja', 'Media', 'Alta', 'Critica')),
    descripcion TEXT NOT NULL,
    recomendacion TEXT,
    UNIQUE (codigo, fecha)
);
CREATE INDEX IF NOT EXISTS idx_hallazgos_fecha ON hallazgos (fecha);
"""


def conectar():
    return sqlite3.connect(DB_PATH)


def crear_tablas():
    with closing(conectar()) as conn:
        conn.executescript(ESQUEMA)
        conn.commit()
    print(f"[+] Base de datos '{DB_PATH}' lista con la tabla 'hallazgos'.")


if __name__ == "__main__":
    crear_tablas()
