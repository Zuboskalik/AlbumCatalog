# Starts the Vite dev server on http://localhost:5173
# Assumes `frontend/node_modules` already exists (`npm install` — see docs/02_PLAN.md, section 4.1).

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location (Join-Path $root "frontend")

npm run dev
