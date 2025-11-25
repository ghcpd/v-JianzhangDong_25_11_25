#!/usr/bin/env bash
set -euo pipefail

LOGS_DIR=logs
mkdir -p ${LOGS_DIR}
rm -f ${LOGS_DIR}/test_run.log || true

if [ -n "${VIRTUAL_ENV:-}" ]; then
  PYBIN=python
else
  if [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
  fi
  PYBIN=python
fi

export API_KEY=DUMMY
export SECRET_KEY=dummy_secret
export DEBUG=False
export TEST_LOG_PATH=${LOGS_DIR}/test_run.log

${PYBIN} tests/test_security.py
EXIT_CODE=$?
exit ${EXIT_CODE}
