#!/data/data/com.termux/files/usr/bin/bash
set -eu
cd "$(dirname "$0")"
if [ ! -d .venv ]; then python -m venv .venv 2>/dev/null || true; fi
if [ -x .venv/bin/python ]; then PY=.venv/bin/python; PIP=.venv/bin/pip; else PY=python; PIP='python -m pip'; fi
$PIP install -r requirements.txt
while true; do
  echo; echo '=== WHATSAPP TRACE X | PHANTOM TEAM ==='
  echo '1 Desktop dashboard'
  echo '2 Terminal mode'
  echo '0 Exit'
  read -r -p 'Select: ' choice
  case "$choice" in
    1) "$PY" app.py ;;
    2) "$PY" terminal.py ;;
    0) exit 0 ;;
    *) echo 'Invalid option.' ;;
  esac
done
