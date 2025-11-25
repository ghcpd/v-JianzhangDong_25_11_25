@echo off
setlocal enabledelayedexpansion
if not exist logs mkdir logs
del /Q logs\test_run.log >nul 2>&1 || echo.

set API_KEY=AKIA_EXAMPLE_HARDCODED_KEY_123456
set SECRET_KEY=dummy_secret
set DEBUG=True
set TEST_LOG_PATH=logs\test_run.log
set EXTERNAL_SERVER=1
powershell -Command "Get-WmiObject Win32_Process | Where-Object { $_.CommandLine -and $_.CommandLine -like '*input_vulnerable.py*' } | ForEach-Object { $_.Terminate() }"

:: Kill any previous instances matching input_vulnerable.py (silently ignore errors)
powershell -Command "Get-WmiObject Win32_Process | Where-Object { $_.CommandLine -and $_.CommandLine -match 'input_vulnerable.py' } | ForEach-Object { try { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue } catch {} }"

:: Start vulnerable server and capture PID via PowerShell
for /f "usebackq" %%i in (`powershell -Command "Start-Process -FilePath 'python' -ArgumentList 'input_vulnerable.py' -PassThru | Select-Object -ExpandProperty Id"`) do set PID=%%i
echo Started input_vulnerable.py with PID %PID%
timeout /t 2 /nobreak >nul
python tests\test_security.py
set EXITCODE=%ERRORLEVEL%
if %EXITCODE% NEQ 0 (
	echo Test run produced vulnerabilities
	type logs\test_run.log
	:: Best-effort stop of lingering processes
	powershell -Command "Get-WmiObject Win32_Process | Where-Object { $_.CommandLine -and $_.CommandLine -match 'input_vulnerable.py' } | ForEach-Object { try { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue } catch {} }"
	exit /b %EXITCODE%
)
:: Best-effort stop of lingering processes
powershell -Command "Get-WmiObject Win32_Process | Where-Object { $_.CommandLine -and $_.CommandLine -match 'input_vulnerable.py' } | ForEach-Object { try { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue } catch {} }"
type logs\test_run.log
exit /b 0
