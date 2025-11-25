@echo off
setlocal enabledelayedexpansion
set "ROOT_DIR=%~dp0"
set "LOG_DIR=%ROOT_DIR%logs"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
set "LOG_FILE=%LOG_DIR%\test_run.log"

set "TMP_CURRENT=%ROOT_DIR%\.tmp_input_current.py"
copy /Y "%ROOT_DIR%\input.py" "%TMP_CURRENT%" >nul

rem 1) Original code should fail tests
copy /Y "%ROOT_DIR%\input_original.py" "%ROOT_DIR%\input.py" >nul
set "USERS_JSON={\"bob\":\"Password1!\"}"
set "CSRF_TOKEN=TEST_CSRF_TOKEN"

echo ===== Tests against ORIGINAL code (expected to FAIL) ===== > "%LOG_FILE%"
python -m pytest -q "%ROOT_DIR%\tests" >> "%LOG_FILE%" 2>&1
if %ERRORLEVEL%==0 (
  echo ERROR: Tests unexpectedly passed against original code. >> "%LOG_FILE%"
  copy /Y "%TMP_CURRENT%" "%ROOT_DIR%\input.py" >nul
  exit /b 1
)

rem 2) Fixed code should pass tests
copy /Y "%ROOT_DIR%\input_fixed.py" "%ROOT_DIR%\input.py" >nul
python -m pytest -q "%ROOT_DIR%\tests" >> "%LOG_FILE%" 2>&1
if not %ERRORLEVEL%==0 (
  echo ERROR: Tests failed against fixed code. >> "%LOG_FILE%"
  copy /Y "%TMP_CURRENT%" "%ROOT_DIR%\input.py" >nul
  exit /b 1
)

copy /Y "%TMP_CURRENT%" "%ROOT_DIR%\input.py" >nul
del "%TMP_CURRENT%" >nul 2>&1

echo All checks completed. Original: FAILED (expected). Fixed: PASSED. >> "%LOG_FILE%"
exit /b 0
