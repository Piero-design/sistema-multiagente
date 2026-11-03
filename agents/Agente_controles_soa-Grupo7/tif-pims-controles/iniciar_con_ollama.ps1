# Script de inicio automatizado con IA local Ollama
# Proyecto: Agente de Evaluación de Controles PIMS (ISO/IEC 27701:2025) - UNSA

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  Iniciando Agente de Controles PIMS con Ollama Local" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$modelo = if ($env:OLLAMA_MODEL) { $env:OLLAMA_MODEL } else { "qwen2.5:0.5b" }

# 1. Verificar si el servicio de Ollama esta activo
Write-Host "`n[1/4] Comprobando servicio de Ollama..." -ForegroundColor Yellow
$ollamaActivo = $false
try {
    $res = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get -TimeoutSec 3 -ErrorAction SilentlyContinue
    if ($res) { $ollamaActivo = $true }
} catch {
    $ollamaActivo = $false
}

if (-not $ollamaActivo) {
    Write-Host "Iniciando servicio de Ollama en segundo plano..." -ForegroundColor Gray
    Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 3
}

# 2. Verificar modelos de IA en Ollama (generativo y embeddings)
Write-Host "`n[2/4] Verificando modelos en Ollama: $modelo (generativo) y all-minilm (embeddings)..." -ForegroundColor Yellow
try {
    $lista = ollama list
    if ($lista -notmatch "qwen2.5") {
        Write-Host "Descargando modelo liviano ($modelo)..." -ForegroundColor Magenta
        ollama pull $modelo
    } else {
        Write-Host "Modelo generativo $modelo listo." -ForegroundColor Green
    }
    if ($lista -notmatch "all-minilm") {
        Write-Host "Descargando modelo de embeddings (all-minilm)..." -ForegroundColor Magenta
        ollama pull all-minilm
    } else {
        Write-Host "Modelo de embeddings all-minilm listo." -ForegroundColor Green
    }
} catch {
    Write-Host "Advertencia: No se pudo verificar con ollama cli. Se intentara conexion directa por API." -ForegroundColor DarkYellow
}

# 3. Iniciar Servidor Web Flask
Write-Host "`n[3/4] Levantando servidor web Flask en http://127.0.0.1:5000..." -ForegroundColor Yellow
$directorioScript = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $directorioScript

# 4. Abrir navegador
Start-Process "http://127.0.0.1:5000"

Write-Host "`n[4/4] Servidor activo. Presiona Ctrl + C para detener." -ForegroundColor Green
python app.py
