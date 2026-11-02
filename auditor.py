import os
import json
from datetime import datetime

OUTPUT_JSON = "hallazgos.json"


def ahora():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def verificar_permisos_criticos():
    archivo = "/etc/shadow"
    hallazgos = []
    try:
        permisos = oct(os.stat(archivo).st_mode)[-3:]
        if int(permisos[2]) > 0:
            hallazgos.append({
                "id_hallazgo": 101,
                "fecha_registro": ahora(),
                "tipo_categoria": "Permisos de Archivo",
                "severidad": "Alta",
                "descripcion": f"El archivo {archivo} posee permisos inseguros ({permisos}).",
                "recomendacion": "Restringir accesos ejecutando: sudo chmod 600 /etc/shadow",
            })
    except PermissionError:
        print("[-] Permisos insuficientes para inspeccionar el archivo.")
    except Exception as e:
        print(f"[-] Error inesperado: {e}")
    return hallazgos


def analizar_logs_auth():
    hallazgos = []
    ruta_log = "/var/log/auth.log"
    if os.path.exists(ruta_log):
        try:
            with open(ruta_log, "r", encoding="utf-8", errors="ignore") as f:
                lineas = f.readlines()
            fallidos = sum(1 for l in lineas if "Failed password" in l and "sshd" in l)
            if fallidos > 0:
                hallazgos.append({
                    "id_hallazgo": 102,
                    "fecha_registro": ahora(),
                    "tipo_categoria": "Analisis de Log",
                    "severidad": "Critica" if fallidos > 5 else "Media",
                    "descripcion": f"Se registraron {fallidos} intentos fallidos de acceso SSH.",
                    "recomendacion": "Habilitar Fail2ban para bloqueo automatico de IPs y deshabilitar el acceso root directo.",
                })
        except PermissionError:
            print("[-] Permisos insuficientes para leer el log. Usa sudo.")
    else:
        print("[-] No se encontro /var/log/auth.log")
    return hallazgos


def main():
    print("[*] Iniciando motor de auditoria DevSecOps...")
    hallazgos_totales = []
    hallazgos_totales.extend(verificar_permisos_criticos())
    hallazgos_totales.extend(analizar_logs_auth())

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(hallazgos_totales, f, indent=4, ensure_ascii=False)

    print(f"[+] Escaneo completado. Archivo '{OUTPUT_JSON}' generado.")


if __name__ == "__main__":
    main()
