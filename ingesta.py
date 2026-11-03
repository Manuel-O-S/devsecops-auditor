import json
import sys
from contextlib import closing

from database import SEVERIDADES, conectar, crear_tablas

INPUT_JSON = "hallazgos.json"

CAMPOS = ("id_hallazgo", "fecha_registro", "tipo_categoria",
          "severidad", "descripcion", "recomendacion")

SQL_INSERT = """
INSERT OR IGNORE INTO hallazgos
    (codigo, fecha, categoria, severidad, descripcion, recomendacion)
VALUES (?, ?, ?, ?, ?, ?)
"""


def cargar_json(ruta):
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            datos = json.load(f)
    except FileNotFoundError:
        sys.exit(f"[-] No se encontro '{ruta}'. Ejecuta primero auditor.py.")
    except json.JSONDecodeError as e:
        sys.exit(f"[-] '{ruta}' no es un JSON valido: {e}")
    if not isinstance(datos, list):
        sys.exit("[-] El contrato exige una lista de hallazgos en la raiz del JSON.")
    return datos


def validar(hallazgo):
    errores = [f"falta '{c}'" for c in CAMPOS if c not in hallazgo]
    if not errores and hallazgo["severidad"] not in SEVERIDADES:
        errores.append(f"severidad desconocida '{hallazgo['severidad']}'")
    return errores


def insertar(hallazgos):
    nuevos = duplicados = invalidos = 0
    with closing(conectar()) as conn:
        for h in hallazgos:
            errores = validar(h)
            if errores:
                print(f"[-] Registro omitido ({', '.join(errores)}): {h}")
                invalidos += 1
                continue
            cursor = conn.execute(SQL_INSERT, (
                h["id_hallazgo"], h["fecha_registro"], h["tipo_categoria"],
                h["severidad"], h["descripcion"], h["recomendacion"],
            ))
            if cursor.rowcount == 1:
                nuevos += 1
            else:
                duplicados += 1
        conn.commit()
    return nuevos, duplicados, invalidos


def main():
    print("[*] Iniciando ingesta de hallazgos...")
    crear_tablas()
    hallazgos = cargar_json(INPUT_JSON)
    if not hallazgos:
        print("[+] El JSON esta vacio: el escaneo no reporto hallazgos.")
        return
    nuevos, duplicados, invalidos = insertar(hallazgos)
    print(f"[+] Ingesta completada: {nuevos} nuevos, "
          f"{duplicados} duplicados ignorados, {invalidos} invalidos.")


if __name__ == "__main__":
    main()
