@echo off
title PDF-flowline - Flow Direction Checker
echo ==========================================
echo   PDF-flowline Starting...
echo ==========================================
echo.

:: Check for venv
if not exist ".\\venv\\Scripts\\python.exe" (
    echo [SETUP] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create venv. Install Python first.
        pause
        exit /b
    )
    echo [SETUP] Installing dependencies ^(PP-OCRv6 local OCR, offline^)...
    ".\\venv\\Scripts\\python.exe" -m pip install paddleocr onnxruntime opencv-python pillow numpy PyQt6 pymupdf
    if errorlevel 1 (
        echo [ERROR] pip install failed.
        pause
        exit /b
    )
    echo [SETUP] Done. First run will download OCR model ^(4.3MB^).
    goto :launch
)

:: Quick check: is paddleocr installed?
".\\venv\\Scripts\\python.exe" -c "import paddleocr" 1>nul 2>&1
if errorlevel 1 (
    echo [SETUP] Installing missing dependencies...
    ".\\venv\\Scripts\\python.exe" -m pip install paddleocr onnxruntime opencv-python pillow numpy PyQt6 pymupdf
    if errorlevel 1 (
        echo [ERROR] pip install failed.
        pause
        exit /b
    )
)

:launch
echo [INFO] PP-OCRv6 tiny_rec ^(local OCR^) - no API key, fully offline.
echo.
".\\venv\\Scripts\\python.exe" ".\\flowline_checker\\main.py"

if errorlevel 1 (
    echo.
    echo [ERROR] Program exited with code %errorlevel%.
    echo.
    pause
)
