#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."

echo
echo "========================================"
echo " ELEVA CAM — site local"
echo "========================================"
echo
echo "Site:   http://127.0.0.1:15000/eleva-cam"
echo "Painel: http://127.0.0.1:15000/cameras"
echo

if command -v python3 >/dev/null 2>&1; then
  exec python3 app.py
fi

if command -v python >/dev/null 2>&1; then
  exec python app.py
fi

echo "[ERRO] Python não encontrado. Instale Python 3.10+ e: pip install flask werkzeug" >&2
exit 1
