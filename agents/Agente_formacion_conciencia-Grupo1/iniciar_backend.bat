@echo off
title Backend - Agente ISO 27701
cd /d "%~dp0backend"

echo ========================================================
echo   Iniciando Backend (FastAPI + ChromaDB + SQLite)
echo ========================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] No se encontro el entorno virtual en backend\.venv
    pause
    exit /b 1
)

echo Usando entorno virtual: backend\.venv
echo.
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000

pause
