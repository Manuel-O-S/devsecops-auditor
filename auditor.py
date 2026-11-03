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


def verificar_permisos_sistema():
    esperados = {"/etc/passwd": 0o644, "/etc/sudoers": 0o440}
    problemas = []
    for archivo, esperado in esperados.items():
        try:
            actual = os.stat(archivo).st_mode & 0o777
            if actual & ~esperado:
                problemas.append(
                    f"{archivo} ({oct(actual)[-3:]}, esperado {oct(esperado)[-3:]})")
        except FileNotFoundError:
            print(f"[-] No se encontro {archivo}")
        except Exception as e:
            print(f"[-] Error inesperado en {archivo}: {e}")
    hallazgos = []
    if problemas:
        hallazgos.append({
            "id_hallazgo": 103,
            "fecha_registro": ahora(),
            "tipo_categoria": "Permisos de Archivo",
            "severidad": "Media",
            "descripcion": "Permisos mas abiertos de lo esperado: " + ", ".join(problemas) + ".",
            "recomendacion": "Corregir con: sudo chmod 644 /etc/passwd y sudo chmod 440 /etc/sudoers",
        })
    return hallazgos


def verificar_usuarios_uid0():
    hallazgos = []
    extras = []
    try:
        with open("/etc/passwd", "r", encoding="utf-8") as f:
            for linea in f:
                partes = linea.strip().split(":")
                if len(partes) >= 3 and partes[2] == "0" and partes[0] != "root":
                    extras.append(partes[0])
    except Exception as e:
        print(f"[-] No se pudo leer /etc/passwd: {e}")
    if extras:
        hallazgos.append({
            "id_hallazgo": 104,
            "fecha_registro": ahora(),
            "tipo_categoria": "Cuentas de Usuario",
            "severidad": "Critica",
            "descripcion": "Usuarios distintos de root con privilegios de administrador (UID 0): " + ", ".join(extras) + ".",
            "recomendacion": "Revisar la cuenta y eliminarla o cambiar su UID, por ejemplo: sudo userdel NOMBRE",
        })
    return hallazgos


def main():
    print("[*] Iniciando motor de auditoria DevSecOps...")
    hallazgos_totales = []
    hallazgos_totales.extend(verificar_permisos_criticos())
    hallazgos_totales.extend(analizar_logs_auth())
    hallazgos_totales.extend(verificar_permisos_sistema())
    hallazgos_totales.extend(verificar_usuarios_uid0())

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(hallazgos_totales, f, indent=4, ensure_ascii=False)

    print(f"[+] Escaneo completado. Archivo '{OUTPUT_JSON}' generado.")


if __name__ == "__main__":
    main()
