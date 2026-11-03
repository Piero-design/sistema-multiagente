$ErrorActionPreference = 'Continue'
Write-Host '== ISO Studio: verificacion local ==' -ForegroundColor Cyan
Write-Host 'Node:'; node --version
Write-Host 'npm:'; npm --version
Write-Host 'Docker:'; docker --version
Write-Host 'Docker Engine:'
docker info --format 'Server={{.ServerVersion}}' 2>$null
Write-Host 'Contenedores:'
docker compose -f (Join-Path $PSScriptRoot '..\infra\compose.yaml') ps
Write-Host 'HTTP local:'
foreach($url in @('http://127.0.0.1:5678','http://127.0.0.1:4317/api/status','http://127.0.0.1:5173')) {
 try {
  $response=Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5
  Write-Host "$url -> HTTP $($response.StatusCode)" -ForegroundColor Green
 } catch {
  Write-Host "$url -> no responde ($($_.Exception.Message))" -ForegroundColor Yellow
 }
}
