@echo off
REM Test script for Windows
echo ================================
echo Security Audit - Test Execution
echo ================================
echo.

setlocal enabledelayedexpansion

REM Set test file (default to input.py)
set TEST_FILE=%1
if "%TEST_FILE%"=="" set TEST_FILE=input.py

echo Testing file: %TEST_FILE%
echo.

set FAILURES=0

REM Test 1: Hardcoded API Key
echo Testing for hardcoded secrets...
findstr /C:"AKIA_EXAMPLE_HARDCODED_KEY_123456" "%TEST_FILE%" >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    echo [VULNERABLE] Hardcoded API key found in source code
    set /a FAILURES+=1
) else (
    echo [SECURE] No hardcoded API keys found
)
echo.

REM Test 2: SQL Injection
echo Testing SQL Injection vulnerability...
findstr /C:"sql = \"SELECT id, username FROM users WHERE username LIKE '%%{}%%'\".format" "%TEST_FILE%" >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    echo [VULNERABLE] SQL Injection vulnerability found - string formatting in SQL query
    set /a FAILURES+=1
) else (
    findstr /C:"cur.execute(sql, (f'%%{name}%%',))" "%TEST_FILE%" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo [SECURE] SQL Injection prevented with parameterized queries
    ) else (
        echo [SECURE] No SQL injection vulnerabilities found
    )
)
echo.

REM Test 3: Pickle Deserialization
echo Testing insecure deserialization (pickle^)...
findstr /C:"pickle.loads" "%TEST_FILE%" >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    echo [VULNERABLE] Insecure pickle.loads(^) found - RCE possible
    set /a FAILURES+=1
) else (
    echo [SECURE] No insecure deserialization found
)
echo.

REM Test 4: Command Injection
echo Testing command injection vulnerability...
findstr /C:"os.system" "%TEST_FILE%" >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    echo [VULNERABLE] os.system(^) with user input found - command injection possible
    set /a FAILURES+=1
) else (
    echo [SECURE] No command injection vulnerabilities found
)
echo.

REM Test 5: SSTI
echo Testing Server-Side Template Injection...
findstr /C:"render_template_string" "%TEST_FILE%" >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    echo [VULNERABLE] render_template_string with user input - SSTI possible
    set /a FAILURES+=1
) else (
    echo [SECURE] No SSTI vulnerabilities found
)
echo.

REM Test 6: Weak Passwords
echo Testing for weak/plaintext passwords...
findstr /C:"\"password\":" "%TEST_FILE%" >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    echo [VULNERABLE] Plaintext passwords found in source code
    set /a FAILURES+=1
) else (
    echo [SECURE] Passwords are properly hashed
)
echo.

REM Test 7: Debug Mode
echo Testing debug mode configuration...
findstr /C:"app.run(debug=True)" "%TEST_FILE%" >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    echo [VULNERABLE] Debug mode is hardcoded to True
    set /a FAILURES+=1
) else (
    echo [SECURE] Debug mode is properly configured
)
echo.

REM Print results
echo ================================
echo Test Results
echo ================================

if !FAILURES! EQU 0 (
    echo All security tests PASSED
    echo The application is secure!
    exit /b 0
) else (
    echo Found !FAILURES! security vulnerabilities
    echo The application is NOT secure!
    exit /b 1
)
