$ErrorActionPreference='Stop'
$Root='C:\Auditoria Agente\iso-studio-7-2-gestion-riesgos'
if (-not (Test-Path $Root)) { throw "No existe $Root" }
Write-Host 'ISO STUDIO 7.2 - ACCESO PUBLICO TEMPORAL SIN CONTRASENA' -ForegroundColor Cyan
& python "$PSScriptRoot\HABILITAR_PUBLICO.py"
if ($LASTEXITCODE -ne 0) { throw 'Error al preparar el backend.' }
Push-Location $Root
try {
    & npm run build
    if ($LASTEXITCODE -ne 0) { throw 'Fallo la compilacion del frontend.' }
    $existing=Get-NetTCPConnection -LocalPort 4317 -State Listen -ErrorAction SilentlyContinue
    if ($existing) { throw 'El puerto 4317 sigue ocupado. Deten el npm run dev anterior con Ctrl+C y vuelve a ejecutar este script.' }
    $node=(Get-Command node -ErrorAction Stop).Source
    $p=Start-Process -FilePath $node -ArgumentList 'server/index.js' -WorkingDirectory $Root -PassThru -RedirectStandardOutput "$Root\.iso-public-stdout.log" -RedirectStandardError "$Root\.iso-public-stderr.log"
    Start-Sleep -Seconds 3
    try { $status=Invoke-RestMethod 'http://127.0.0.1:4317/api/status' -TimeoutSec 8 }
    catch { throw 'El servidor no respondio en 4317. Revisa .iso-public-stderr.log.' }
    if ($status.scope.mode -ne 'public_testing' -or $status.scope.n8nReviewed -ne $false) { throw "Estado inesperado: $($status.scope | ConvertTo-Json -Compress)" }
    $docTest=Invoke-WebRequest 'http://127.0.0.1:4317/PLAN_PRUEBAS_ISO_STUDIO_7_2.docx' -Method Head -UseBasicParsing -TimeoutSec 8
    if ($docTest.StatusCode -ne 200) {throw 'El Word no esta disponible desde la web.'}
    Write-Host 'Backend y documento listos. Generando link publico...' -ForegroundColor Green
    $cmd=Get-Command cloudflared -ErrorAction SilentlyContinue
    if (-not $cmd) { $cmd=Get-Command cloudflared.exe -ErrorAction SilentlyContinue }
    $cloud = if ($cmd) { $cmd.Source } else { $null }
    if (-not $cloud) {
        $places=@('C:\Auditoria Agente\cloudflared.exe',"$env:LOCALAPPDATA\Microsoft\WinGet\Links\cloudflared.exe",'C:\Program Files (x86)\cloudflared\cloudflared.exe','C:\Program Files\cloudflared\cloudflared.exe')
        $cloud=$places | Where-Object { Test-Path $_ } | Select-Object -First 1
    }
    if (-not $cloud) {throw 'No encontre cloudflared. Instala con winget install --id Cloudflare.cloudflared -e y vuelve a ejecutar el script (deten primero el servidor que inicio).'}
    Write-Host 'Comparte la URL https://XXXXX.trycloudflare.com que aparece abajo.' -ForegroundColor Yellow
    Write-Host 'Documento: AGREGA /PLAN_PRUEBAS_ISO_STUDIO_7_2.docx al final de la misma URL.' -ForegroundColor Yellow
    Write-Host 'Deja abierta esta ventana. Ctrl+C cierra el enlace publico.' -ForegroundColor Yellow
    & $cloud tunnel --url http://127.0.0.1:4317
} finally { Pop-Location }
