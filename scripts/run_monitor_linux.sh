#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
pip install -r requirements.txt >/dev/null

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Se creó .env desde .env.example. Edita .env antes de ejecutar en producción."
fi

python src/cardmarket_monitor.py --env-file .env --ignored-file ignored_cards.txt --verbose
