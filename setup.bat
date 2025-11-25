@echo off
REM Setup script for Windows environments

setlocal enabledelayedexpansion

echo.
echo === Flask Application Security Audit Setup ===
echo.

REM Check Python version
python --version
if !errorlevel! neq 0 (
    echo [ERROR] Python not found in PATH
    exit /b 1
)

REM Create virtual environment
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if !errorlevel! equ 0 (
        echo [OK] Virtual environment created
    ) else (
        echo [ERROR] Failed to create virtual environment
        exit /b 1
    )
) else (
    echo [OK] Virtual environment already exists
)

REM Activate virtual environment
call venv\Scripts\activate.bat
if !errorlevel! neq 0 (
    echo [ERROR] Failed to activate virtual environment
    exit /b 1
)
echo [OK] Virtual environment activated

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip setuptools wheel >nul 2>&1
if !errorlevel! equ 0 (
    echo [OK] pip upgraded
) else (
    echo [WARN] pip upgrade may have issues
)

REM Install dependencies
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt >nul 2>&1
if !errorlevel! equ 0 (
    echo [OK] Dependencies installed
) else (
    echo [ERROR] Failed to install dependencies
    exit /b 1
)

REM Create logs directory
if not exist logs mkdir logs
echo [OK] Logs directory created

echo.
echo === Setup Complete ===
echo.
echo To activate the environment, run:
echo   venv\Scripts\activate.bat
echo.
echo To run tests, execute:
echo   run_test.bat
echo     or
echo   python test_automation.py
echo.
echo To run the Flask app:
echo   python input.py
echo.

exit /b 0
