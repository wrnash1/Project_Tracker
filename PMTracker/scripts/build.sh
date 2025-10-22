#!/bin/bash

# Build script for PM Project Tracker (Linux/Mac)

echo "================================"
echo "PM Project Tracker - Build Script"
echo "================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# Build the application
echo "Building application with PyInstaller..."
pyinstaller build.spec --clean --noconfirm

# Check if build was successful
if [ -f "dist/PMTracker/PMTracker" ]; then
    echo
    echo "================================"
    echo "Build completed successfully!"
    echo "================================"
    echo
    echo "Executable location: dist/PMTracker/PMTracker"
    echo
else
    echo
    echo "================================"
    echo "Build FAILED!"
    echo "================================"
    echo
fi
