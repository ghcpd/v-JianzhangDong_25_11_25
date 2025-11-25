#!/usr/bin/env bash
set -euo pipefail

LOGS_DIR=logs
mkdir -p ${LOGS_DIR}
rm -f ${LOGS_DIR}/test_run.log

if [ -n "${VIRTUAL_ENV:-}" ]; then
  PYBIN=python
else
  if [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
  fi
  PYBIN=python
fi

export API_KEY=AKIA_EXAMPLE_HARDCODED_KEY_123456
export SECRET_KEY=dummy_secret
export DEBUG=True
export EXTERNAL_SERVER=1

${PYBIN} input_vulnerable.py &
PID=$!
sleep 2
export TEST_LOG_PATH=${LOGS_DIR}/test_run.log
${PYBIN} tests/test_security.py || true
RET=$?
kill ${PID} || true
if [ ${RET} -ne 0 ]; then
  echo "Test run detected vulnerabilities" >&2
  exit ${RET}
fi
exit 0
