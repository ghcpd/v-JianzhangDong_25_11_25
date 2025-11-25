#!/usr/bin/env sh
set -eu
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"
python3 -m pytest -q
