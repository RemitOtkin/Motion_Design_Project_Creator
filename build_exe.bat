@echo off
rem Builds dist\ProjectCreator\ProjectCreator.exe with PyInstaller.
cd /d "%~dp0"
python -m pip install --user pyinstaller -r requirements.txt || exit /b 1
python -m PyInstaller --noconfirm --windowed --name ProjectCreator --icon resources\img\icon.ico --add-data "resources;resources" main.py
echo.
echo Done: dist\ProjectCreator\ProjectCreator.exe
pause
