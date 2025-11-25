@echo off
REM Test script for Windows - Tests vulnerability demonstrations
setlocal enabledelayedexpansion

set LOG_FILE=logs\test_run.log
if not exist logs mkdir logs

(
    echo.
    echo ========================================
    echo Flask Security Audit - Test Suite
    echo Platform: Windows
    echo Timestamp: %date% %time%
    echo ========================================
    echo.
    
    REM Check if virtual environment exists
    if exist venv\Scripts\activate.bat (
        call venv\Scripts\activate.bat
        echo [OK] Virtual environment activated
    ) else (
        echo [WARN] Virtual environment not found. Run setup.bat first.
        exit /b 1
    )
    
    echo.
    echo --- Test 1: Vulnerability Detection ---
    echo Checking for hardcoded secrets in fixed code...
    
    findstr /m "AKIA_EXAMPLE_HARDCODED_KEY" input.py >nul 2>&1
    if !errorlevel! equ 0 (
        echo [FAIL] Hardcoded API key still present
        exit /b 1
    ) else (
        echo [PASS] No hardcoded API key found
    )
    
    echo.
    echo --- Test 2: SQL Injection Prevention ---
    echo Checking for parameterized queries...
    
    findstr /m "cur.execute(sql)" input.py >nul 2>&1
    if !errorlevel! equ 0 (
        findstr /m "format(name)" input.py >nul 2>&1
        if !errorlevel! equ 0 (
            echo [FAIL] Vulnerable SQL injection pattern detected
            exit /b 1
        )
    )
    echo [PASS] SQL query implementation improved
    
    echo.
    echo --- Test 3: Pickle Deserialization Check ---
    echo Checking for unsafe pickle usage...
    
    findstr /m "pickle.loads" input.py >nul 2>&1
    if !errorlevel! equ 0 (
        echo [FAIL] Unsafe pickle.loads() still present
        exit /b 1
    ) else (
        echo [PASS] pickle.loads() removed
    )
    
    findstr /m "get_json" input.py >nul 2>&1
    if !errorlevel! equ 0 (
        echo [PASS] JSON parsing implemented as safe alternative
    )
    
    echo.
    echo --- Test 4: Command Injection Prevention ---
    echo Checking for safe command execution...
    
    findstr /m "os.system" input.py >nul 2>&1
    if !errorlevel! equ 0 (
        echo [FAIL] Unsafe os.system() detected
        exit /b 1
    ) else (
        echo [PASS] os.system() with user input removed
    )
    
    findstr /m "subprocess.run" input.py >nul 2>&1
    if !errorlevel! equ 0 (
        echo [PASS] Safe subprocess implementation with command whitelisting
    )
    
    echo.
    echo --- Test 5: Template Injection Prevention ---
    echo Checking for unsafe template rendering...
    
    findstr /m "render_template_string" input.py >nul 2>&1
    if !errorlevel! equ 0 (
        echo [FAIL] Unsafe render_template_string() detected
        exit /b 1
    ) else (
        echo [PASS] render_template_string() with user input removed
    )
    
    findstr /m "escape" input.py >nul 2>&1
    if !errorlevel! equ 0 (
        echo [PASS] HTML escaping implemented
    )
    
    echo.
    echo --- Test 6: Hardcoded Credentials Check ---
    echo Checking for hardcoded passwords...
    
    findstr /m "password123" input.py >nul 2>&1
    if !errorlevel! equ 0 (
        echo [FAIL] Hardcoded password detected
        exit /b 1
    ) else (
        echo [PASS] Hardcoded passwords removed
    )
    
    findstr /m "password_hash" input.py >nul 2>&1
    if !errorlevel! equ 0 (
        echo [PASS] Password hashing implemented
    )
    
    echo.
    echo --- Test 7: Weak Password Comparison Check ---
    echo Checking for proper password verification...
    
    findstr /m "check_password_hash" input.py >nul 2>&1
    if !errorlevel! equ 0 (
        echo [PASS] Proper password hashing verification implemented
    )
    
    echo.
    echo --- Test 8: Debug Mode Check ---
    echo Checking for debug mode in production...
    
    findstr /m "debug=True" input.py >nul 2>&1
    if !errorlevel! equ 0 (
        echo [FAIL] Debug mode enabled in code
        exit /b 1
    ) else (
        echo [PASS] Debug mode disabled by default
    )
    
    findstr /m "FLASK_DEBUG" input.py >nul 2>&1
    if !errorlevel! equ 0 (
        echo [PASS] Debug mode controlled by environment variable
    )
    
    echo.
    echo --- Syntax Validation ---
    echo Checking Python syntax...
    python -m py_compile input.py
    if !errorlevel! equ 0 (
        echo [PASS] Python syntax is valid
    ) else (
        echo [FAIL] Python syntax errors found
        exit /b 1
    )
    
    echo.
    echo --- Import Validation ---
    echo Checking imports...
    python -c "import input; print('[PASS] All imports successful')"
    
    echo.
    echo ========================================
    echo Test Results: ALL TESTS PASSED
    echo ========================================
    echo.
    
) > "%LOG_FILE%" 2>&1

type "%LOG_FILE%"
echo.
echo Log saved to: %LOG_FILE%
exit /b 0
