#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"
PYTHON_BIN=${PYTHON_BIN:-python3}

# Optional: create virtualenv
if [ ! -d .venv ]; then
  $PYTHON_BIN -m venv .venv
fi
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

mkdir -p logs
chmod +x run_test.sh
