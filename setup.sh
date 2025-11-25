#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$ROOT_DIR/.venv"

python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

pip install --upgrade pip
pip install -r "$ROOT_DIR/requirements.txt"

echo "Virtual environment created at $VENV_DIR and dependencies installed."
echo "Run tests with: source $VENV_DIR/bin/activate && bash run_test.sh"
