#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
PYTHON_BIN="$(command -v python3 || command -v python)"
if [ ! -d .venv ]; then
  "$PYTHON_BIN" -m venv .venv 2>/dev/null || true
fi
if [ -f .venv/bin/activate ]; then
  source .venv/bin/activate
  PYTHON_BIN="$(command -v python)"
fi
"$PYTHON_BIN" -m pip install -q -r requirements.txt
while true; do
  echo
  echo '=========================================='
  echo ' WHATSAPP TRACE X | PHANTOM TEAM'
  echo '=========================================='
  echo '1) Desktop mode (local web dashboard)'
  echo '2) Terminal mode (menu-driven CLI)'
  echo '0) Exit'
  read -r -p 'Select mode: ' mode
  case "$mode" in
    1) "$PYTHON_BIN" app.py; break ;;
    2) "$PYTHON_BIN" terminal.py ;;
    0) exit 0 ;;
    *) echo 'Invalid option.' ;;
  esac
done
