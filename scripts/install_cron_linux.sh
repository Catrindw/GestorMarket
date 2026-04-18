#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="$ROOT_DIR/.venv/bin/python3"
LOG_FILE="$ROOT_DIR/logs/cardmarket-monitor.log"

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "No existe $PYTHON_BIN. Ejecuta primero: bash scripts/run_monitor_linux.sh" >&2
  exit 1
fi

mkdir -p "$ROOT_DIR/logs"

tmpfile="$(mktemp)"
cat > "$tmpfile" <<CRON
# Cardmarket monitor (instalado automáticamente)
0 8 * * * cd $ROOT_DIR && $PYTHON_BIN src/cardmarket_monitor.py --env-file .env --ignored-file ignored_cards.txt >> $LOG_FILE 2>&1
30 16 * * * cd $ROOT_DIR && $PYTHON_BIN src/cardmarket_monitor.py --env-file .env --ignored-file ignored_cards.txt >> $LOG_FILE 2>&1
CRON

crontab "$tmpfile"
rm -f "$tmpfile"

echo "Cron instalado para $ROOT_DIR"
crontab -l
