@echo off
if not exist logs mkdir logs
set LOGFILE=logs\test_run.log
echo TEST RUN - %DATE% %TIME% > %LOGFILE%

if not exist input_fixed.py (
  copy input.py input_fixed.py >nul
)

if not exist input_vulnerable.py (
  echo ERROR: no input_vulnerable.py found to test the original vulnerable version >> %LOGFILE%
  exit /b 2
)

echo Running tests against ORIGINAL (vulnerable) version... >> %LOGFILE%
copy /Y input_vulnerable.py input.py >nul
python -m pytest -q >> %LOGFILE% 2>&1
set ORIGINAL_STATUS=%ERRORLEVEL%
if %ORIGINAL_STATUS% EQU 0 (
  >>%LOGFILE% echo ERROR: tests unexpectedly passed against vulnerable/original source - expected failures
  exit /b 10
)
>>%LOGFILE% echo As expected, tests failed against the original vulnerable source - exit %ORIGINAL_STATUS%

echo Restoring patched app and re-running tests (should pass)... >> %LOGFILE%
copy /Y input_fixed.py input.py >nul
python -m pytest -q >> %LOGFILE% 2>&1
set PATCHED_STATUS=%ERRORLEVEL%
if %PATCHED_STATUS% NEQ 0 (
  >>%LOGFILE% echo ERROR: tests failed against patched source - exit %PATCHED_STATUS%
  exit /b 20
)

echo All checks passed against patched version. >> %LOGFILE%
exit /b 0
