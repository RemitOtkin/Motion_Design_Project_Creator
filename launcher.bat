@echo off
title Project Creator
cd /d "%~dp0"

where python >nul 2>&1
if errorlevel 1 (
    echo Python was not found. Install Python 3.10+ from https://www.python.org/downloads/
    echo and tick "Add Python to PATH" during setup.
    pause
    exit /b 1
)

python -c "import PySide6" >nul 2>&1
if errorlevel 1 (
    echo Installing PySide6 ^(first run only^)...
    python -m pip install --user -r requirements.txt
    if errorlevel 1 (
        echo Could not install PySide6.
        pause
        exit /b 1
    )
)

start "" pythonw main.py
