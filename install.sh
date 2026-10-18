#!/usr/bin/env bash
# One-command setup for Linux, macOS and Termux (Android).
cd "$(dirname "$0")" || exit 1
echo "== Veda AI setup =="

PY=python3
command -v python3 >/dev/null 2>&1 || PY=python
if ! command -v "$PY" >/dev/null 2>&1; then
  echo "Python is not installed. Install it first (Termux: pkg install python)."; exit 1
fi

case "$PREFIX" in *com.termux*) TERMUX=1;; *) TERMUX=0;; esac

if [ "$TERMUX" = "0" ]; then
  echo "-> Creating a virtual environment (.venv)"
  $PY -m venv .venv && . .venv/bin/activate && PY=python
fi

echo "-> Installing Python packages"
$PY -m pip install -r requirements.txt || { echo "Package install failed."; exit 1; }

if [ ! -f .env ]; then
  cp .env.example .env
  echo "-> Created .env  (open it and paste your GROQ_API_KEY)"
fi

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "-> ffmpeg not found. It is optional (only for unusual audio/video formats). Trying to install it..."
  if [ "$TERMUX" = "1" ]; then pkg install -y ffmpeg || echo "   Skipped. If you see a CANNOT LINK error, run: pkg upgrade -y"
  elif command -v apt-get >/dev/null 2>&1; then sudo apt-get install -y ffmpeg || true
  elif command -v brew >/dev/null 2>&1; then brew install ffmpeg || true
  fi
  if ! command -v ffmpeg >/dev/null 2>&1 && [ "$TERMUX" = "0" ]; then
    $PY -m pip install -r requirements-optional.txt || true
  fi
fi

echo
echo "Done. Next:"
echo "  1) Edit .env and paste your key:   nano .env"
echo "  2) Start the app:                  ./start.sh   (or: python app.py)"
