#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: Python 3 is required. Install it with: sudo apt install python3 python3-venv"
  exit 1
fi

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi

if [[ "${1:-}" == "--test" ]]; then
  .venv/bin/python -m unittest discover -s tests -v
  exit $?
fi

if [[ "${1:-}" == "--demo" ]]; then
  .venv/bin/python -m src.main --demo
  exit $?
fi

if [[ ! -f .venv/.deps_installed ]]; then
  .venv/bin/python -m pip install --upgrade pip
  .venv/bin/python -m pip install -r requirements.txt
  touch .venv/.deps_installed
fi

exec .venv/bin/python -m src.main
