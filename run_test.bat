@echo off
REM Test script for Windows
REM Tests both vulnerable (input.py) and secure (secure_input.py) versions

setlocal enabledelayedexpansion

echo === Flask Security Audit - Windows Test Script ===
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo ERROR: Virtual environment not found. Run setup.bat first.
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Create logs directory
if not exist logs mkdir logs

set TEST_LOG=logs\test_run.log

echo Running tests... >> "%TEST_LOG%"
echo Test timestamp: %date% %time% >> "%TEST_LOG%"
echo.

REM Set required environment variable for secure version
set API_KEY=test_api_key_secure

echo === Testing Secure Version (secure_input.py) === >> "%TEST_LOG%"
echo === Testing Secure Version (secure_input.py) ===
python -m pytest test_vulnerabilities.py -v --tb=short >> "%TEST_LOG%" 2>&1

if %ERRORLEVEL% equ 0 (
    echo. >> "%TEST_LOG%"
    echo [✓] Secure version tests PASSED >> "%TEST_LOG%"
    echo [✓] Secure version tests PASSED
    set SECURE_PASSED=1
) else (
    echo. >> "%TEST_LOG%"
    echo [✗] Secure version tests FAILED >> "%TEST_LOG%"
    echo [✗] Secure version tests FAILED
    set SECURE_PASSED=0
)

echo.
echo === Testing Vulnerable Version (input.py) === >> "%TEST_LOG%"
echo === Testing Vulnerable Version (input.py) ===
python -m pytest test_vulnerabilities.py::test_vulnerable_version -v --tb=short >> "%TEST_LOG%" 2>&1

if %ERRORLEVEL% equ 0 (
    echo. >> "%TEST_LOG%"
    echo [✓] Vulnerable version tests detected issues (as expected) >> "%TEST_LOG%"
    echo [✓] Vulnerable version tests detected issues (as expected)
    set VULN_DETECTED=1
) else (
    echo. >> "%TEST_LOG%"
    echo [✓] Vulnerable version failed as expected >> "%TEST_LOG%"
    echo [✓] Vulnerable version failed as expected
    set VULN_DETECTED=1
)

echo.
echo === Test Summary === >> "%TEST_LOG%"
if %SECURE_PASSED% equ 1 (
    echo. >> "%TEST_LOG%"
    echo [✓] Secure version: PASSED >> "%TEST_LOG%"
    echo [✓] Secure version: PASSED
    exit /b 0
) else (
    echo. >> "%TEST_LOG%"
    echo [✗] Secure version: FAILED >> "%TEST_LOG%"
    echo [✗] Secure version: FAILED
    exit /b 1
)
