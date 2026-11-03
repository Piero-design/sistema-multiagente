#!/usr/bin/env bash
# Script de inicio automatizado con IA local Ollama para macOS / Linux
# Proyecto: Agente de Evaluación de Controles PIMS (ISO/IEC 27701:2025) - UNSA

echo "=========================================================="
echo "  Iniciando Agente de Controles PIMS con Ollama Local"
echo "=========================================================="

# 1. Comprobar si Ollama está activo
echo ""
echo "[1/3] Comprobando servicio de Ollama..."
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "Iniciando servicio de Ollama en segundo plano..."
    ollama serve > /dev/null 2>&1 &
    sleep 3
else
    echo "Servicio Ollama activo."
fi

# 2. Directorio del script y entorno virtual
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

PYTHON_BIN="$DIR/.venv/bin/python"
if [ ! -f "$PYTHON_BIN" ]; then
    PYTHON_BIN="python3"
fi

# 3. Iniciar Servidor Web Flask
echo ""
echo "[2/3] Levantando servidor web Flask en http://127.0.0.1:5000..."
echo ""
echo "[3/3] Abriendo navegador..."
open "http://127.0.0.1:5000" 2>/dev/null || true

echo "Servidor activo. Presiona Ctrl + C para detener."
"$PYTHON_BIN" app.py
