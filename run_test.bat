@echo off
REM Windows test execution script

echo === Flask Security Test Suite - Windows ===
echo.

REM Create logs directory
if not exist logs mkdir logs

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found. Run setup.bat first.
    echo Attempting to run with system Python...
)

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found!
    exit /b 1
)

REM Check if required files exist
if not exist input.py (
    echo Error: input.py not found!
    exit /b 1
)

if not exist input_secure.py (
    echo Error: input_secure.py not found!
    exit /b 1
)

if not exist test_vulnerabilities.py (
    echo Error: test_vulnerabilities.py not found!
    exit /b 1
)

REM Install requirements if needed
echo Checking dependencies...
python -m pip install -q -r requirements.txt

REM Create test database
echo Setting up test database...
python -c "import sqlite3; conn = sqlite3.connect('users.db'); cur = conn.cursor(); cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT)'); cur.execute('DELETE FROM users'); cur.execute('INSERT INTO users VALUES (1, \"testuser\")'); cur.execute('INSERT INTO users VALUES (2, \"admin\")'); conn.commit(); conn.close()" 2>nul

echo.
echo Starting security tests...
echo Logs will be saved to: logs\test_run.log
echo.

REM Run tests
python test_vulnerabilities.py

REM Capture exit code
set EXIT_CODE=%ERRORLEVEL%

echo.
if %EXIT_CODE% EQU 0 (
    echo === ALL TESTS PASSED ===
) else (
    echo === TESTS FAILED ===
)

echo Check logs\test_run.log for detailed results
exit /b %EXIT_CODE%
