$root='C:\Auditoria Agente\iso-studio-7-2-gestion-riesgos'
$envpath=Join-Path $root '.env'
$lines=Get-Content $envpath | Where-Object { $_ -notmatch '^\s*(SCOPE_PUBLIC_TESTING|SCOPE_LOCAL_TESTING|SCOPE_N8N_REVIEWED)\s*=' }
$content=($lines -join "`r`n")+"`r`nSCOPE_N8N_REVIEWED=false`r`nSCOPE_LOCAL_TESTING=true`r`nSCOPE_PUBLIC_TESTING=false`r`n"
[System.IO.File]::WriteAllText($envpath,$content,[System.Text.UTF8Encoding]::new($false))
Write-Host 'Bandera publica deshabilitada. Cierra cloudflared y REINICIA el backend para aplicar el cambio.'
