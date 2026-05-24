@echo off
chcp 1251 >nul
title Contour Extractor

set "APP_DIR=%~dp0"
set "VENV_DIR=%APP_DIR%venv"
set "PYTHON_SCRIPT=%APP_DIR%app.py"
set "MARKER=%VENV_DIR%\.installed"

python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  ОШИБКА: Python не найден!
    echo.
    echo  Скачайте Python: https://www.python.org/downloads/
    echo  При установке поставьте галочку "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

if not exist "%MARKER%" (
    echo.
    echo  ПЕРВЫЙ ЗАПУСК - установка библиотек...
    echo  Подождите 1-2 минуты.
    echo.

    if exist "%VENV_DIR%" rmdir /s /q "%VENV_DIR%"

    echo  [1/3] Создаём виртуальное окружение...
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo  ОШИБКА: не удалось создать venv.
        pause
        exit /b 1
    )

    echo  [2/3] Обновляем pip...
    "%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip --quiet

    echo  [3/3] Устанавливаем библиотеки...
    "%VENV_DIR%\Scripts\pip.exe" install opencv-python pillow customtkinter numpy
    if errorlevel 1 (
        echo  ОШИБКА: не удалось установить библиотеки.
        echo  Проверьте интернет и запустите снова.
        pause
        exit /b 1
    )

    echo installed > "%MARKER%"
    echo.
    echo  Установка завершена!
    echo.
)

echo  Запускаем приложение...
"%VENV_DIR%\Scripts\pythonw.exe" "%PYTHON_SCRIPT%"
if errorlevel 1 (
    "%VENV_DIR%\Scripts\python.exe" "%PYTHON_SCRIPT%"
    pause
)
