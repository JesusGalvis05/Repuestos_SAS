$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
python scripts/configure.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
if (-not (Test-Path -LiteralPath '.venv/Scripts/python.exe')) {
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
& ./.venv/Scripts/python.exe -m pip install -r backend/requirements-dev.lock
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& ./.venv/Scripts/python.exe -m pip install --no-deps -e ./backend
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Push-Location -LiteralPath frontend
try { npm.cmd ci; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE } } finally { Pop-Location }
Write-Host 'Entorno preparado. Consulte README.md para migraciones y administrador.'
