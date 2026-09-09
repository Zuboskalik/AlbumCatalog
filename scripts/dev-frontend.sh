#!/usr/bin/env bash
# Starts the Vite dev server on http://localhost:5173
# Assumes frontend/node_modules already exists (`npm install` — see docs/02_PLAN.md, section 4.1).
set -euo pipefail
cd "$(dirname "$0")/../frontend"
npm run dev
