@echo on
echo --- DEBUG START ---
if not exist logs mkdir logs
echo created logs? %ERRORLEVEL%
set LOGFILE=logs\test_run.log
echo LOGFILE set to %LOGFILE%
echo TEST RUN - %DATE% %TIME% > %LOGFILE%
echo after write TEST RUN ERR %ERRORLEVEL%

if not exist input_fixed.py (
  echo input_fixed.py missing -> copying
  copy input.py input_fixed.py >nul
  echo copied
)

if not exist input_vulnerable.py (
  echo missing vulnerable file
  echo ERROR: no input_vulnerable.py found to test the original vulnerable version >> %LOGFILE%
  exit /b 2
)

echo Running tests against ORIGINAL (vulnerable) version... >> %LOGFILE%
copy /Y input_vulnerable.py input.py >nul
echo after copy, err %ERRORLEVEL%
python -m pytest -q >> %LOGFILE% 2>&1
echo pytest ran, err %ERRORLEVEL%
set ORIGINAL_STATUS=%ERRORLEVEL%
if %ORIGINAL_STATUS% EQU 0 (
  >>%LOGFILE% echo ERROR: tests unexpectedly passed against vulnerable/original source - expected failures
  exit /b 10
)
>>%LOGFILE% echo As expected, tests failed against the original vulnerable source - exit %ORIGINAL_STATUS%

echo Restoring patched app and re-running tests (should pass)... >> %LOGFILE%
copy /Y input_fixed.py input.py >nul
echo after restore err %ERRORLEVEL%
python -m pytest -q >> %LOGFILE% 2>&1
echo pytest ran for patched version err %ERRORLEVEL%
set PATCHED_STATUS=%ERRORLEVEL%
if %PATCHED_STATUS% NEQ 0 (
  >>%LOGFILE% echo ERROR: tests failed against patched source - exit %PATCHED_STATUS%
  exit /b 20
)

echo All checks passed against patched version. >> %LOGFILE%
echo --- DEBUG END ---
exit /b 0
