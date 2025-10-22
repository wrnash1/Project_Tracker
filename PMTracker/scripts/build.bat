@echo off
REM Build script for PM Project Tracker (Windows)

echo ================================
echo PM Project Tracker - Build Script
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

REM Build the application
echo Building application with PyInstaller...
pyinstaller build.spec --clean --noconfirm

REM Check if build was successful
if exist "dist\PMTracker\PMTracker.exe" (
    echo.
    echo ================================
    echo Build completed successfully!
    echo ================================
    echo.
    echo Executable location: dist\PMTracker\PMTracker.exe
    echo.
) else (
    echo.
    echo ================================
    echo Build FAILED!
    echo ================================
    echo.
)

pause
