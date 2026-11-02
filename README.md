# DevSecOps Auditor

Sistema de auditoría de seguridad para Linux: un escáner en Python revisa permisos de archivos críticos y registros de autenticación, guarda los hallazgos en una base de datos y los muestra en un dashboard.

Flujo: Script de escaneo -> JSON -> SQLite -> Dashboard (Streamlit)

## Estado del proyecto

- [x] Motor de escaneo (auditor.py) y contrato JSON
- [ ] Base de datos e ingesta
- [ ] Dashboard
- [ ] Automatización del pipeline

## Requisitos

- Ubuntu 22.04 LTS (probado en una máquina virtual)
- Python 3.10 o superior

## Cómo ejecutar el escáner

    git clone https://github.com/Manuel-O-S/devsecops-auditor.git
    cd devsecops-auditor
    python3 -m venv venv
    source venv/bin/activate
    sudo python3 auditor.py

Se genera el archivo hallazgos.json (se usa sudo para poder leer archivos protegidos).

## Qué detecta el escáner

| Código | Chequeo | Severidad |
|---|---|---|
| 101 | Permisos inseguros en /etc/shadow | Alta |
| 102 | Intentos fallidos de acceso SSH en /var/log/auth.log | Media o Crítica (más de 5 intentos) |

## Formato del JSON (contrato de datos)

Lista de objetos con las llaves: id_hallazgo, fecha_registro, tipo_categoria, severidad, descripcion y recomendacion.

## Pruebas realizadas

Un sistema recién instalado no tiene hallazgos, así que se provocaron a propósito (solo en una VM de práctica):
- Permisos abiertos en /etc/shadow con chmod 644, restaurados después a 640.
- Intentos fallidos simulados con el comando logger.

Los datos de hallazgos.json en el repositorio son datos de prueba.

## Problemas encontrados y soluciones

- Falsos positivos en el conteo: el escáner contaba también comandos sudo que mencionaban la frase buscada. Solución: contar solo las líneas del servicio sshd.
- Líneas repetidas compactadas: rsyslog agrupa mensajes idénticos en una sola línea ("message repeated N times"), lo que hacía subestimar los intentos. En ataques reales cada intento suele traer un puerto distinto, por lo que no se agrupan.

## Limitaciones y mejoras futuras

- El escáner cuenta líneas, no interpreta los mensajes agrupados por rsyslog.
- No distingue direcciones IP de origen ni ventanas de tiempo.
- Solo revisa un archivo crítico; se pueden agregar más (por ejemplo /etc/passwd).

## Base de datos, dashboard y pipeline

(Pendiente)

## Autor

- Manuel-O-S
