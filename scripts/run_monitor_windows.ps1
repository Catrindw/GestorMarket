$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-Not (Test-Path ".venv")) {
  py -3 -m venv .venv
}

& .\.venv\Scripts\python.exe -m pip install -r requirements.txt | Out-Null

if (-Not (Test-Path ".env")) {
  Copy-Item .env.example .env
  Write-Host "Se creó .env desde .env.example. Edita .env antes de ejecutar en producción."
}

& .\.venv\Scripts\python.exe src\cardmarket_monitor.py --env-file .env --ignored-file ignored_cards.txt --verbose
