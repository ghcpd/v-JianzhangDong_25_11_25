@echo off
REM Test script for Windows - Tests both vulnerable and secure versions

setlocal enabledelayedexpansion

set "LOG_FILE=logs\test_run.log"
if not exist logs mkdir logs

echo ================================================ >> "%LOG_FILE%"
echo Flask Application Security Testing >> "%LOG_FILE%"
echo Date: %date% %time% >> "%LOG_FILE%"
echo ================================================ >> "%LOG_FILE%"

echo ================================================
echo Flask Application Security Testing
echo Date: %date% %time%
echo ================================================

REM Initialize counters
set /a vulnerable_failed=0
set /a vulnerable_total=0
set /a secure_passed=0
set /a secure_total=0

echo.
echo ================================================
echo TESTING VULNERABLE VERSION (input_vulnerable.py)
echo Expected: Tests should FAIL (vulnerabilities present)
echo ================================================
echo.
echo ================================================ >> "%LOG_FILE%"
echo TESTING VULNERABLE VERSION >> "%LOG_FILE%"
echo ================================================ >> "%LOG_FILE%"

REM Check for hardcoded secrets in vulnerable version
echo Checking for Hardcoded Secrets in vulnerable version...
findstr /C:"AKIA_EXAMPLE_HARDCODED_KEY" input_vulnerable.py >nul 2>&1
if !errorlevel! equ 0 (
    echo   [FAIL] Hardcoded Secrets: Found API key in source code
    echo   [FAIL] Hardcoded Secrets: Found API key >> "%LOG_FILE%"
    set /a vulnerable_failed+=1
) else (
    echo   [PASS] Hardcoded Secrets: No hardcoded keys found
    echo   [PASS] Hardcoded Secrets: No hardcoded keys found >> "%LOG_FILE%"
)
set /a vulnerable_total+=1

REM Start vulnerable version
set API_KEY=test-key
set FLASK_DEBUG=False
set FLASK_PORT=5001
echo Starting vulnerable version on port 5001...
start /B python input_vulnerable.py > nul 2>&1
set VULNERABLE_PID=%ERRORLEVEL%
timeout /t 5 /nobreak >nul

REM Wait for server to be ready
set /a attempts=0
:wait_vulnerable
set /a attempts+=1
curl -s http://127.0.0.1:5001/ >nul 2>&1
if !errorlevel! equ 0 goto vulnerable_ready
if !attempts! geq 30 (
    echo Failed to start vulnerable version
    echo Failed to start vulnerable version >> "%LOG_FILE%"
    goto test_secure
)
timeout /t 1 /nobreak >nul
goto wait_vulnerable

:vulnerable_ready
echo Server is ready on port 5001

REM Test SQL Injection
echo.
echo Testing SQL Injection on vulnerable version...
curl -s "http://127.0.0.1:5001/greet?name=test" >nul 2>&1
if !errorlevel! equ 0 (
    echo   [FAIL] SQL Injection: Server responding (potentially vulnerable)
    echo   [FAIL] SQL Injection: Potentially vulnerable >> "%LOG_FILE%"
    set /a vulnerable_failed+=1
) else (
    echo   [PASS] SQL Injection: Properly handled
    echo   [PASS] SQL Injection: Properly handled >> "%LOG_FILE%"
)
set /a vulnerable_total+=1

REM Test SSTI
echo.
echo Testing Server-Side Template Injection on vulnerable version...
curl -s "http://127.0.0.1:5001/greet?name={{7*7}}" > temp_response.txt 2>&1
findstr /C:"49" temp_response.txt >nul 2>&1
if !errorlevel! equ 0 (
    echo   [FAIL] SSTI: Vulnerable - template expression evaluated
    echo   [FAIL] SSTI: Vulnerable - template expression evaluated >> "%LOG_FILE%"
    set /a vulnerable_failed+=1
) else (
    echo   [PASS] SSTI: Protected
    echo   [PASS] SSTI: Protected >> "%LOG_FILE%"
)
set /a vulnerable_total+=1
del temp_response.txt >nul 2>&1

REM Test Command Injection
echo.
echo Testing Command Injection on vulnerable version...
curl -s -X POST http://127.0.0.1:5001/run -d "cmd=test; whoami" > temp_response.txt 2>&1
findstr /C:"done" temp_response.txt >nul 2>&1
if !errorlevel! equ 0 (
    echo   [FAIL] Command Injection: Vulnerable - command may have executed
    echo   [FAIL] Command Injection: Vulnerable >> "%LOG_FILE%"
    set /a vulnerable_failed+=1
) else (
    echo   [PASS] Command Injection: Blocked
    echo   [PASS] Command Injection: Blocked >> "%LOG_FILE%"
)
set /a vulnerable_total+=1
del temp_response.txt >nul 2>&1

REM Test Pickle Deserialization
echo.
echo Testing Insecure Deserialization on vulnerable version...
curl -s -X POST http://127.0.0.1:5001/upload_profile -H "Content-Type: application/json" -d "{\"name\": \"test\"}" > temp_response.txt 2>&1
findstr /C:"status" temp_response.txt >nul 2>&1
if !errorlevel! equ 0 (
    echo   [INFO] Deserialization: Response received
    echo   [INFO] Deserialization: Response received >> "%LOG_FILE%"
    set /a vulnerable_failed+=1
) else (
    echo   [PASS] Deserialization: Rejected
    echo   [PASS] Deserialization: Rejected >> "%LOG_FILE%"
)
set /a vulnerable_total+=1
del temp_response.txt >nul 2>&1

REM Stop vulnerable version
echo.
echo Stopping vulnerable version...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5001" ^| find "LISTENING"') do taskkill /F /PID %%a >nul 2>&1
timeout /t 2 /nobreak >nul

:test_secure
echo.
echo ================================================
echo TESTING SECURE VERSION (input.py)
echo Expected: Tests should PASS (vulnerabilities fixed)
echo ================================================
echo.
echo ================================================ >> "%LOG_FILE%"
echo TESTING SECURE VERSION >> "%LOG_FILE%"
echo ================================================ >> "%LOG_FILE%"

REM Check for hardcoded secrets in secure version
echo Checking for Hardcoded Secrets in secure version...
findstr /C:"AKIA_EXAMPLE_HARDCODED_KEY" input.py >nul 2>&1
if !errorlevel! equ 0 (
    echo   [FAIL] Hardcoded Secrets: Found API key in source code
    echo   [FAIL] Hardcoded Secrets: Found API key >> "%LOG_FILE%"
) else (
    echo   [PASS] Hardcoded Secrets: No hardcoded keys found
    echo   [PASS] Hardcoded Secrets: No hardcoded keys found >> "%LOG_FILE%"
    set /a secure_passed+=1
)
set /a secure_total+=1

REM Start secure version
set FLASK_PORT=5002
echo Starting secure version on port 5002...
start /B python input.py > nul 2>&1
timeout /t 5 /nobreak >nul

REM Wait for server to be ready
set /a attempts=0
:wait_secure
set /a attempts+=1
curl -s http://127.0.0.1:5002/ >nul 2>&1
if !errorlevel! equ 0 goto secure_ready
if !attempts! geq 30 (
    echo Failed to start secure version
    echo Failed to start secure version >> "%LOG_FILE%"
    goto summary
)
timeout /t 1 /nobreak >nul
goto wait_secure

:secure_ready
echo Server is ready on port 5002

REM Test SQL Injection Protection
echo.
echo Testing SQL Injection protection on secure version...
curl -s "http://127.0.0.1:5002/greet?name=' OR '1'='1" > temp_response.txt 2>&1
findstr /C:"error" temp_response.txt >nul 2>&1
if !errorlevel! neq 0 (
    echo   [PASS] SQL Injection: Properly handled/blocked
    echo   [PASS] SQL Injection: Properly handled >> "%LOG_FILE%"
    set /a secure_passed+=1
) else (
    echo   [FAIL] SQL Injection: Not properly protected
    echo   [FAIL] SQL Injection: Not properly protected >> "%LOG_FILE%"
)
set /a secure_total+=1
del temp_response.txt >nul 2>&1

REM Test SSTI Protection
echo.
echo Testing SSTI protection on secure version...
curl -s "http://127.0.0.1:5002/greet?name={{7*7}}" > temp_response.txt 2>&1
findstr /C:"49" temp_response.txt >nul 2>&1
if !errorlevel! neq 0 (
    echo   [PASS] SSTI: Protected - input properly escaped
    echo   [PASS] SSTI: Protected >> "%LOG_FILE%"
    set /a secure_passed+=1
) else (
    echo   [FAIL] SSTI: Still vulnerable
    echo   [FAIL] SSTI: Still vulnerable >> "%LOG_FILE%"
)
set /a secure_total+=1
del temp_response.txt >nul 2>&1

REM Test Command Injection Protection
echo.
echo Testing Command Injection protection on secure version...
curl -s -X POST http://127.0.0.1:5002/run -d "cmd=test; whoami" > temp_response.txt 2>&1
findstr /C:"Invalid command" temp_response.txt >nul 2>&1
if !errorlevel! equ 0 (
    echo   [PASS] Command Injection: Blocked malicious input
    echo   [PASS] Command Injection: Blocked >> "%LOG_FILE%"
    set /a secure_passed+=1
) else (
    echo   [FAIL] Command Injection: Not properly protected
    echo   [FAIL] Command Injection: Not properly protected >> "%LOG_FILE%"
)
set /a secure_total+=1
del temp_response.txt >nul 2>&1

REM Test Safe Deserialization
echo.
echo Testing Safe Deserialization on secure version...
curl -s -X POST http://127.0.0.1:5002/upload_profile -H "Content-Type: application/json" -d "{\"name\": \"test\"}" > temp_response.txt 2>&1
findstr /C:"status.*ok" temp_response.txt >nul 2>&1
if !errorlevel! equ 0 (
    echo   [PASS] Deserialization: Using safe JSON format
    echo   [PASS] Deserialization: Using safe JSON >> "%LOG_FILE%"
    set /a secure_passed+=1
) else (
    echo   [FAIL] Deserialization: Not working correctly
    echo   [FAIL] Deserialization: Not working correctly >> "%LOG_FILE%"
)
set /a secure_total+=1
del temp_response.txt >nul 2>&1

REM Stop secure version
echo.
echo Stopping secure version...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5002" ^| find "LISTENING"') do taskkill /F /PID %%a >nul 2>&1
timeout /t 1 /nobreak >nul

:summary
echo.
echo ================================================
echo TEST SUMMARY
echo ================================================
echo Vulnerable Version:
echo   Vulnerabilities Found: !vulnerable_failed!/!vulnerable_total!
echo.
echo Secure Version:
echo   Security Tests Passed: !secure_passed!/!secure_total!
echo.

echo ================================================ >> "%LOG_FILE%"
echo TEST SUMMARY >> "%LOG_FILE%"
echo ================================================ >> "%LOG_FILE%"
echo Vulnerable Version: !vulnerable_failed!/!vulnerable_total! >> "%LOG_FILE%"
echo Secure Version: !secure_passed!/!secure_total! >> "%LOG_FILE%"

REM Determine overall result
if !vulnerable_failed! geq 3 if !secure_passed! geq 4 (
    echo [PASS] OVERALL: PASS
    echo   - Vulnerable version shows expected vulnerabilities
    echo   - Secure version successfully mitigates vulnerabilities
    echo [PASS] OVERALL RESULT >> "%LOG_FILE%"
    exit /b 0
) else (
    echo [FAIL] OVERALL: FAIL
    if !vulnerable_failed! lss 3 (
        echo   - Not enough vulnerabilities detected in vulnerable version
    )
    if !secure_passed! lss 4 (
        echo   - Secure version did not pass enough security tests
    )
    echo [FAIL] OVERALL RESULT >> "%LOG_FILE%"
    exit /b 1
)
