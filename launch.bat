@echo off
title PDF-flowline - Flow Direction Checker
echo ==========================================
echo   PDF-flowline Starting...
echo ==========================================
echo.

:: Check for venv
if not exist ".\\venv\\Scripts\\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo Please ensure the venv directory exists in the project root.
    echo Run: python -m venv venv; venv\Scripts\pip install -r requirements.txt
    echo.
    pause
    exit /b
)

:: Launch main program
".\\venv\\Scripts\\python.exe" ".\\flowline_checker\\main.py"

:: Keep window open on error
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] The program exited with an error (code: %errorlevel%).
    echo.
    pause
)
