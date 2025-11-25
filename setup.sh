#!/usr/bin/env bash
set -euo pipefail

python -m venv .venv
.venv\Scripts\activate 2>/dev/null || . .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Environment prepared. Run ./run_test.sh to execute the tests." 
