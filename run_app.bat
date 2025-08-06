@echo off
echo TextLab Launcher
echo =========================

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7 or later from https://python.org
    pause
    exit /b 1
)

echo.
echo Installing/Updating required packages...
pip install Pillow>=8.0.0
if errorlevel 1 (
    echo Warning: Could not install packages automatically
    echo You may need to run: pip install Pillow
    echo.
)

echo.
echo Starting TextLab...
python textlab.py
if errorlevel 1 (
    echo.
    echo Error: TextLab failed to start
    echo Please check that Python and required packages are installed
    echo.
    echo Try running: python test_startup.py
    echo.
)

echo.
echo TextLab has closed.
pause
