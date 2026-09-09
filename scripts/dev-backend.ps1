# Starts the Django dev server on http://localhost:8000
# Assumes `backend/.venv` already exists (see docs/02_PLAN.md, section 4.1, to create it).

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location (Join-Path $root "backend")

& ".venv\Scripts\python.exe" manage.py runserver 8000
