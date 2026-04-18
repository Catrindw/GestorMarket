#!/usr/bin/env bash
set -euo pipefail

# Uso:
#   bash scripts/run_monitor_auto_linux.sh
#   bash scripts/run_monitor_auto_linux.sh /ruta/al/repo

provided_path="${1:-}"

find_repo() {
  local candidate

  if [[ -n "$provided_path" ]]; then
    if [[ -f "$provided_path/src/cardmarket_monitor.py" ]]; then
      printf '%s\n' "$provided_path"
      return 0
    fi
    echo "Ruta proporcionada inválida: $provided_path" >&2
    return 1
  fi

  for candidate in \
    "$PWD" \
    "$PWD/GestorMarket" \
    "$HOME/GestorMarket" \
    "$HOME/workspace/GestorMarket" \
    "/workspace/GestorMarket" \
    "/workspace/default/GestorMarket"; do
    if [[ -f "$candidate/src/cardmarket_monitor.py" ]]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done

  # Búsqueda limitada en rutas comunes (sin escanear todo el disco)
  while IFS= read -r candidate; do
    printf '%s\n' "$(dirname "$(dirname "$candidate")")"
    return 0
  done < <(find "$HOME" /workspace /opt 2>/dev/null -maxdepth 5 -type f -path '*/src/cardmarket_monitor.py')

  return 1
}

ROOT_DIR="$(find_repo || true)"

if [[ -z "$ROOT_DIR" ]]; then
  cat >&2 <<'MSG'
No encontré automáticamente el repositorio de GestorMarket.
Ejecuta con ruta explícita:
  bash scripts/run_monitor_auto_linux.sh /ruta/real/GestorMarket
MSG
  exit 1
fi

cd "$ROOT_DIR"
echo "Usando repositorio: $ROOT_DIR"

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
