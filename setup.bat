@echo off
REM Setup script for Windows
REM This script sets up the development environment for the Flask security audit project

setlocal enabledelayedexpansion

echo === Flask Security Audit - Windows Setup ===
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.8+ from https://www.python.org
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo Python version: !PYTHON_VERSION!
echo.

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
) else (
    echo Virtual environment already exists.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip --quiet

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt --quiet

REM Create logs directory
if not exist logs mkdir logs

echo.
echo === Setup Complete ===
echo.
echo To activate the environment in future sessions, run:
echo   venv\Scripts\activate.bat
echo.
echo To run tests, execute:
echo   run_test.bat
echo.
echo Or run automatic tests:
echo   python run_tests.py
echo.
