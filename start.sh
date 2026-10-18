#!/usr/bin/env bash
cd "$(dirname "$0")" || exit 1
[ -d .venv ] && . .venv/bin/activate
PY=python3; command -v python3 >/dev/null 2>&1 || PY=python
exec $PY app.py
