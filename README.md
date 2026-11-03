# DevSecOps Auditor

Sistema de auditoría de seguridad para Linux: un escáner en Python revisa permisos de archivos críticos, cuentas de usuario y registros de autenticación, guarda los hallazgos en una base de datos SQLite y los muestra en un dashboard de Streamlit con un puntaje global de riesgo.

Flujo: Script de escaneo -> JSON -> SQLite -> Dashboard (Streamlit)

Proyecto personal para practicar administración de Linux (Ubuntu), seguridad básica y automatización.

## Estado del proyecto

- [x] Motor de escaneo (auditor.py) y contrato JSON
- [x] Base de datos e ingesta (database.py, ingesta.py)
- [x] Dashboard (app.py)
- [x] Automatización del pipeline (run_pipeline.sh)

## Requisitos

- Ubuntu 22.04 LTS (probado en una máquina virtual con VirtualBox)
- Python 3.10 o superior
- Git

## Instalación y ejecución

    git clone https://github.com/Manuel-O-S/devsecops-auditor.git
    cd devsecops-auditor
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ./run_pipeline.sh
    streamlit run app.py

El pipeline ejecuta el escáner con sudo (necesario para leer archivos protegidos) y carga los resultados en seguridad.db. El dashboard queda en http://localhost:8501. Si ejecutas un nuevo escaneo, pulsa "Recargar datos" en la barra lateral.

## Qué detecta el escáner

| Código | Chequeo | Severidad |
|---|---|---|
| 101 | Permisos inseguros en /etc/shadow | Alta |
| 102 | Intentos fallidos de acceso SSH en /var/log/auth.log | Media o Crítica (más de 5 intentos) |
| 103 | Permisos más abiertos de lo esperado en /etc/passwd y /etc/sudoers | Media |
| 104 | Usuarios distintos de root con UID 0 | Crítica |

## Formato del JSON (contrato de datos)

Lista de objetos con las llaves: id_hallazgo, fecha_registro, tipo_categoria, severidad, descripcion y recomendacion. El id_hallazgo identifica el tipo de chequeo, no un evento único.

## Base de datos

SQLite (seguridad.db), tabla hallazgos con id autoincremental, codigo, fecha, categoria, severidad, descripcion y recomendacion. Una restricción UNIQUE (codigo, fecha) evita duplicar un mismo escaneo, y un CHECK limita las severidades a Baja, Media, Alta y Critica. La base se regenera desde hallazgos.json y no se versiona.

## Dashboard

- Puntaje global de riesgo de 0 a 100, calculado con el último registro de cada chequeo (Crítica 50, Alta 30, Media 15, Baja 5, con tope de 100).
- Gráfico de pastel por severidad y barras por categoría.
- Filtros por severidad y categoría, y tabla de detalle con recomendaciones.

## Pruebas realizadas

Un sistema recién instalado no tiene hallazgos, así que se provocaron a propósito, solo en una VM de práctica:
- Permisos abiertos en /etc/shadow (chmod 644) y /etc/passwd (chmod 664), restaurados después.
- Una cuenta falsa con UID 0, eliminada al terminar.
- Intentos fallidos de SSH simulados con el comando logger.

Los datos de hallazgos.json en el repositorio son datos de prueba.

## Problemas encontrados y soluciones

- Falsos positivos en el conteo: el escáner contaba también comandos sudo que mencionaban la frase buscada. Solución: contar solo las líneas del servicio sshd.
- Líneas repetidas compactadas: rsyslog agrupa mensajes idénticos en una sola línea ("message repeated N times"), lo que hacía subestimar los intentos. En ataques reales cada intento suele traer un puerto distinto.
- Rotación de logs: Ubuntu rota auth.log cada semana y los eventos antiguos pasan a auth.log.1, así que el conteo bajó a cero hasta simular nuevos intentos.
- Un id de hallazgo por chequeo: dos hallazgos con el mismo código y fecha chocan con la regla UNIQUE, por lo que los permisos de /etc/passwd y /etc/sudoers se reportan juntos en el 103.

## Limitaciones y mejoras futuras

- El escáner cuenta líneas y no interpreta los mensajes agrupados por rsyslog.
- Solo lee el auth.log actual, no los archivos rotados.
- No distingue direcciones IP de origen ni ventanas de tiempo.
- El dashboard no diferencia un hallazgo resuelto de uno que simplemente no se volvió a escanear.
- Posibles chequeos nuevos: puertos abiertos, intentos fallidos de sudo, servicios activos.

## Autor

Manuel-O-S
