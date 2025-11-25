@echo off
REM Test runner for Windows
REM Tests both vulnerable and fixed versions

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set LOG_DIR=%SCRIPT_DIR%logs
set LOG_FILE=%LOG_DIR%\test_run.log

REM Create logs directory
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM Initialize log
(
    echo ==========================================
    echo Flask Security Audit - Test Suite
    echo Started: %DATE% %TIME%
    echo Platform: Windows
    echo ==========================================
    echo.
) > "%LOG_FILE%"

set test_passed=0
set test_failed=0

echo Testing Flask Application Security Audit
echo. >> "%LOG_FILE%"

REM Test 1: Check if input.py has SQL injection vulnerability
echo Test 1: Vulnerable Version - SQL Injection Detection
find /c ".format(name)" "%SCRIPT_DIR%input.py" > nul 2>&1
if %errorlevel% equ 0 (
    echo   PASSED - vulnerable code found >> "%LOG_FILE%"
    set /a test_passed=!test_passed!+1
) else (
    echo   FAILED - vulnerable code not found >> "%LOG_FILE%"
    set /a test_failed=!test_failed!+1
)
echo. >> "%LOG_FILE%"

REM Test 2: Check if input.py has pickle vulnerability
echo Test 2: Vulnerable Version - Pickle Deserialization Detection
find /c "pickle.loads" "%SCRIPT_DIR%input.py" > nul 2>&1
if %errorlevel% equ 0 (
    echo   PASSED - vulnerable code found >> "%LOG_FILE%"
    set /a test_passed+=1
) else (
    echo   FAILED - vulnerable code not found >> "%LOG_FILE%"
    set /a test_failed+=1
)
echo. >> "%LOG_FILE%"

REM Test 3: Check if input.py has command injection vulnerability
echo Test 3: Vulnerable Version - Command Injection Detection
find /c "os.system" "%SCRIPT_DIR%input.py" > nul 2>&1
if %errorlevel% equ 0 (
    echo   PASSED - vulnerable code found >> "%LOG_FILE%"
    set /a test_passed+=1
) else (
    echo   FAILED - vulnerable code not found >> "%LOG_FILE%"
    set /a test_failed+=1
)
echo. >> "%LOG_FILE%"

REM Test 4: Check if input.py has hardcoded API key
echo Test 4: Vulnerable Version - Hardcoded API Key Detection
find /c "AKIA_EXAMPLE_HARDCODED_KEY" "%SCRIPT_DIR%input.py" > nul 2>&1
if %errorlevel% equ 0 (
    echo   PASSED - hardcoded key found >> "%LOG_FILE%"
    set /a test_passed+=1
) else (
    echo   FAILED - hardcoded key not found >> "%LOG_FILE%"
    set /a test_failed+=1
)
echo. >> "%LOG_FILE%"

REM Test 5: Check if input_fixed.py exists
echo Test 5: Fixed Version - File Exists
if exist "%SCRIPT_DIR%input_fixed.py" (
    echo   PASSED - input_fixed.py found >> "%LOG_FILE%"
    set /a test_passed+=1
) else (
    echo   FAILED - input_fixed.py not found >> "%LOG_FILE%"
    set /a test_failed+=1
)
echo. >> "%LOG_FILE%"

REM Test 6: Check if input_fixed.py uses parameterized queries
echo Test 6: Fixed Version - Parameterized Queries Used
find /c "cur.execute(sql, (" "%SCRIPT_DIR%input_fixed.py" > nul 2>&1
if %errorlevel% equ 0 (
    echo   PASSED - parameterized queries found >> "%LOG_FILE%"
    set /a test_passed+=1
) else (
    echo   FAILED - parameterized queries not found >> "%LOG_FILE%"
    set /a test_failed+=1
)
echo. >> "%LOG_FILE%"

REM Test 7: Check if input_fixed.py uses JSON instead of pickle
echo Test 7: Fixed Version - JSON Instead of Pickle
find /c "get_json" "%SCRIPT_DIR%input_fixed.py" > nul 2>&1
if %errorlevel% equ 0 (
    echo   PASSED - JSON used >> "%LOG_FILE%"
    set /a test_passed+=1
) else (
    echo   FAILED - JSON not found >> "%LOG_FILE%"
    set /a test_failed+=1
)
echo. >> "%LOG_FILE%"

REM Test 8: Check if input_fixed.py uses subprocess instead of os.system
echo Test 8: Fixed Version - Subprocess Instead of os.system
find /c "subprocess.run" "%SCRIPT_DIR%input_fixed.py" > nul 2>&1
if %errorlevel% equ 0 (
    echo   PASSED - subprocess used >> "%LOG_FILE%"
    set /a test_passed+=1
) else (
    echo   FAILED - subprocess not found >> "%LOG_FILE%"
    set /a test_failed+=1
)
echo. >> "%LOG_FILE%"

REM Test 9: Check if input_fixed.py loads API key from environment
echo Test 9: Fixed Version - API Key from Environment
find /c "os.getenv('API_KEY'" "%SCRIPT_DIR%input_fixed.py" > nul 2>&1
if %errorlevel% equ 0 (
    echo   PASSED - API key from environment >> "%LOG_FILE%"
    set /a test_passed+=1
) else (
    echo   FAILED - API key not from environment >> "%LOG_FILE%"
    set /a test_failed+=1
)
echo. >> "%LOG_FILE%"

REM Test 10: Check if input_fixed.py uses password hashing
echo Test 10: Fixed Version - Password Hashing
find /c "generate_password_hash" "%SCRIPT_DIR%input_fixed.py" > nul 2>&1
if %errorlevel% equ 0 (
    echo   PASSED - password hashing found >> "%LOG_FILE%"
    set /a test_passed+=1
) else (
    echo   FAILED - password hashing not found >> "%LOG_FILE%"
    set /a test_failed+=1
)
echo. >> "%LOG_FILE%"

REM Test 11: Check if report.json exists
echo Test 11: Report Generation
if exist "%SCRIPT_DIR%report.json" (
    echo   PASSED - report.json found >> "%LOG_FILE%"
    set /a test_passed+=1
) else (
    echo   FAILED - report.json not found >> "%LOG_FILE%"
    set /a test_failed+=1
)
echo. >> "%LOG_FILE%"

REM Summary
(
    echo.
    echo ==========================================
    echo Test Summary
    echo ==========================================
    echo Passed: %test_passed%
    echo Failed: %test_failed%
    echo Total:  %test_passed% + %test_failed%
    echo.
    if %test_failed% equ 0 (
        echo Status: ALL TESTS PASSED
    ) else (
        echo Status: SOME TESTS FAILED
    )
    echo.
    echo Log file: %LOG_FILE%
    echo Completed: %DATE% %TIME%
    echo ==========================================
) >> "%LOG_FILE%"

echo.
echo Test Summary:
echo Passed: %test_passed%
echo Failed: %test_failed%
echo.
if %test_failed% equ 0 (
    echo Status: ALL TESTS PASSED
    exit /b 0
) else (
    echo Status: SOME TESTS FAILED
    exit /b 1
)
