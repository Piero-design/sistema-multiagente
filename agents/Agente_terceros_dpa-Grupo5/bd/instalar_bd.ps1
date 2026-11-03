# =============================================================================
# instalar_bd.ps1 — Fases 2, 3, 4 y 7 del plan (bd/PLAN_MIGRACION_BD.md) en un paso.
#
#   powershell -ExecutionPolicy Bypass -File bd\instalar_bd.ps1
#   powershell -ExecutionPolicy Bypass -File bd\instalar_bd.ps1 -Base gestitel_revision -Puerto 5432
#
# Pide la contraseña de postgres y las de los roles agente7 y agente7_lectura. No las guarda en
# ningún archivo: solo viven en este proceso. Si la base ya existe, no la recrea; el resto de los
# pasos es idempotente.
# =============================================================================
param(
    [string]$Base = "gestitel_revision",
    [string]$Servidor = "localhost",
    [int]$Puerto = 5432,
    [string]$Esquema = "demo",
    [string]$ScriptProfesor = (Join-Path $PSScriptRoot "gestitel_base_de_datos.sql"),
    [switch]$SinMigrar
)
$ErrorActionPreference = "Stop"
# psql y Python escriben UTF-8: sin esto, Windows PowerShell 5.1 muestra los acentos rotos
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$OutputEncoding = [Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"

function Leer-Clave([string]$texto) {
    $s = Read-Host $texto -AsSecureString
    [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($s))
}
function Paso([string]$t) { Write-Host ""; Write-Host "== $t" -ForegroundColor Cyan }

# psql: PATH o la instalación de EDB
$bin = $null
if (Get-Command psql -ErrorAction SilentlyContinue) { $bin = Split-Path (Get-Command psql).Source }
else {
    foreach ($v in 18, 17, 16) {
        if (Test-Path "C:\Program Files\PostgreSQL\$v\bin\psql.exe") { $bin = "C:\Program Files\PostgreSQL\$v\bin"; break }
    }
}
if (-not $bin) { throw "No encuentro psql. Instala PostgreSQL (fase 1) o agrega su carpeta bin al PATH." }
$env:PATH = "$bin;$env:PATH"
$ver = (& psql --version) -replace '[^\d\.]', ''
Write-Host "psql $ver en $bin"
# El script del profesor lo generó pg_dump 18.4 y usa \restrict: requiere psql 18, 17.6+, 16.10+ o 15.14+.
$p = $ver.Split('.'); $may = [int]$p[0]; $men = [int]$p[1]
if (($may -eq 17 -and $men -lt 6) -or ($may -eq 16 -and $men -lt 10) -or ($may -eq 15 -and $men -lt 14) -or $may -lt 15) {
    throw "psql $ver no entiende \restrict del script del profesor. Actualiza a PostgreSQL 17.6+ (o 16.10+)."
}
if (-not (Test-Path $ScriptProfesor)) { throw "No encuentro el script del profesor: $ScriptProfesor" }

$env:PGHOST = $Servidor; $env:PGPORT = "$Puerto"; $env:PGCLIENTENCODING = "UTF8"
$env:PGPASSWORD = Leer-Clave "Contraseña del usuario postgres"
$claveAgente = Leer-Clave "Contraseña nueva para el rol agente7 (n8n)"
$claveLectura = Leer-Clave "Contraseña nueva para el rol agente7_lectura (chat)"

try {
    Paso "Fase 2 · Base $Base con el script del profesor"
    $existe = & psql -X -U postgres -d postgres -Atc "SELECT 1 FROM pg_database WHERE datname = '$Base'"
    if ($LASTEXITCODE -ne 0) { throw "No pude conectarme a PostgreSQL en ${Servidor}:$Puerto." }
    if ($existe -eq "1") {
        Write-Host "La base $Base ya existe: no se recrea."
    } else {
        & createdb -U postgres -E UTF8 $Base; if ($LASTEXITCODE -ne 0) { throw "createdb falló." }
        & psql -X -q -U postgres -d $Base -f $ScriptProfesor | Out-Null; if ($LASTEXITCODE -ne 0) { throw "Falló el script del profesor." }
    }
    & psql -X -U postgres -d $Base -Atc "SELECT table_schema || ': ' || count(*) FROM information_schema.tables WHERE table_schema IN ('public','$Esquema') AND table_type = 'BASE TABLE' GROUP BY table_schema"

    Paso "Fase 3 · Extensión del Agente 7"
    & psql -X -q -U postgres -d $Base -v schema=$Esquema -f (Join-Path $PSScriptRoot "agente7_terceros_dpa.sql")
    if ($LASTEXITCODE -ne 0) { throw "Falló la extensión del Agente 7." }

    Paso "Fase 4 · Usuarios autores y roles"
    & psql -X -q -U postgres -d $Base -v schema=$Esquema -v clave_agente7=$claveAgente -v clave_lectura=$claveLectura `
        -f (Join-Path $PSScriptRoot "roles_agente7.sql")
    if ($LASTEXITCODE -ne 0) { throw "Falló la creación de roles." }

    if (-not $SinMigrar) {
        Paso "Fase 7 · Migración de los expedientes existentes"
        $env:PGUSER = "postgres"; $env:PGDATABASE = $Base
        & python (Join-Path $PSScriptRoot "migrar_registros.py") --esquema $Esquema
    }

    Paso "Pruebas de reglas del motor"
    & psql -X -q -U postgres -d $Base -f (Join-Path $PSScriptRoot "pruebas\02_reglas.sql")
} finally {
    Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
}
Write-Host ""
Write-Host "Listo. Siguiente: credencial 'PIMS Postgres' en n8n con el usuario agente7 (fase 5)." -ForegroundColor Green
