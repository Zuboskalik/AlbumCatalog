#!/usr/bin/env bash
# Starts the Django dev server on http://localhost:8000
# Assumes backend/.venv already exists (see docs/02_PLAN.md, section 4.1, to create it).
set -euo pipefail
cd "$(dirname "$0")/../backend"
source .venv/Scripts/activate 2>/dev/null || source .venv/bin/activate
python manage.py runserver 8000
