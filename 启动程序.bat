@echo off
title Flowline Direction Checker
echo ==========================================
echo   Flowline Direction Checker Starting...
echo ==========================================
echo.

:: 检查 venv 是否存在
if not exist ".\venv\Scripts\python.exe" (
    echo [错误] 找不到虚拟环境 venv！
    echo 请确保当前文件夹下有 venv 目录。
    echo.
    pause
    exit /b
)

:: 运行主程序
".\venv\Scripts\python.exe" ".\flowline_checker\main.py"

:: 如果程序异常退出，保留窗口显示错误
if %errorlevel% neq 0 (
    echo.
    echo [错误] 程序运行中发生崩溃信息如上。
    echo.
    pause
)
