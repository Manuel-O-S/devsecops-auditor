#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

echo "[*] 1/2 Ejecutando auditor.py con privilegios elevados..."
sudo python3 auditor.py
sudo chown "$USER":"$USER" hallazgos.json

echo "[*] 2/2 Ingestando hallazgos en seguridad.db..."
venv/bin/python ingesta.py

echo "[+] Pipeline completado. Dashboard: venv/bin/streamlit run app.py"
