@echo off
:: Project Creator - Простой надежный launcher
title Project Creator
color 0A
chcp 65001 >nul

:: Переходим в папку со скриптом
cd /d "%~dp0"

echo.
echo ████████████████████████████████████████████████████
echo █                                                  █
echo █        🎬 PROJECT CREATOR LAUNCHER 🎬          █
echo █                                                  █
echo ████████████████████████████████████████████████████
echo.

:: Проверяем Python
echo [1/3] 🐍 Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден!
    echo.
    echo 💡 Установите Python 3.7+ с https://www.python.org/downloads/
    echo ⚠️  При установке отметьте "Add Python to PATH"
    echo.
    pause
    exit /b 1
)
echo ✅ Python найден

:: Проверяем основные файлы
echo.
echo [2/3] 📁 Проверка файлов...
if not exist "main.py" (
    echo ❌ main.py не найден!
    pause
    exit /b 1
)
echo ✅ main.py найден

:: Проверяем зависимости
echo.
echo [3/3] 📚 Проверка зависимостей...
python -c "import PyQt5" >nul 2>&1
if errorlevel 1 (
    echo ❌ PyQt5 не найден, устанавливаем...
    python -m pip install PyQt5 --user
    if errorlevel 1 (
        echo ❌ Ошибка установки PyQt5
        pause
        exit /b 1
    )
    echo ✅ PyQt5 установлен
) else (
    echo ✅ PyQt5 найден
)

:: Запуск приложения
echo.
echo ████████████████████████████████████████████████████
echo █              🚀 ЗАПУСК ПРИЛОЖЕНИЯ 🚀           █
echo ████████████████████████████████████████████████████
echo.

python main.py

if errorlevel 1 (
    echo.
    echo ❌ Приложение завершилось с ошибкой
    pause
) else (
    echo.
    echo ✅ Приложение завершено успешно
)

echo.
echo 👋 Спасибо за использование Project Creator!
timeout /t 3 /nobreak >nul