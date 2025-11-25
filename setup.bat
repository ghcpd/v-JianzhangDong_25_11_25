@echo off
REM Setup script for Windows environments

echo === Flask Security Audit - Environment Setup (Windows) ===
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed. Please install Python 3.8 or higher.
    exit /b 1
)

python --version

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt

REM Create logs directory
echo Creating logs directory...
if not exist logs mkdir logs

REM Create database for testing
echo Creating test database...
python -c "import sqlite3; conn = sqlite3.connect('users.db'); cur = conn.cursor(); cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT)'); cur.execute('INSERT OR IGNORE INTO users VALUES (1, \"testuser\")'); cur.execute('INSERT OR IGNORE INTO users VALUES (2, \"admin\")'); conn.commit(); conn.close(); print('Database initialized.')"

echo.
echo === Setup Complete ===
echo To activate the environment, run: venv\Scripts\activate.bat
echo To run tests, execute: run_test.bat
echo.
pause
