@echo off
setlocal enabledelayedexpansion
if not exist logs mkdir logs
del /Q logs\test_run.log >nul 2>&1 || echo.

set API_KEY=DUMMY
set SECRET_KEY=dummy_secret
set DEBUG=False
set TEST_LOG_PATH=logs\test_run.log
:: Ensure no lingering vulnerable server
powershell -Command "Get-WmiObject Win32_Process | Where-Object { $_.CommandLine -and $_.CommandLine -like '*input_vulnerable.py*' } | ForEach-Object { $_.Terminate() }"

python tests\test_security.py
if %ERRORLEVEL% neq 0 (
    type logs\test_run.log
    exit /b %ERRORLEVEL%
)
type logs\test_run.log
exit /b 0
