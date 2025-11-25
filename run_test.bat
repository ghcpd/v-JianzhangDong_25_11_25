@echo off
setlocal enabledelayedexpansion
cd /d %~dp0
python -m pytest -q
if ERRORLEVEL 1 exit /b %ERRORLEVEL%
