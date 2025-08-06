# Font Image Maker Launcher (PowerShell)
Write-Host "Font Image Maker Launcher" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Green

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.7 or later from https://python.org" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Install/Update packages
Write-Host "`nInstalling/Updating required packages..." -ForegroundColor Yellow
try {
    pip install "Pillow>=8.0.0"
    Write-Host "Dependencies installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "Warning: Could not install dependencies automatically" -ForegroundColor Yellow
    Write-Host "You may need to run: pip install Pillow" -ForegroundColor Yellow
}

# Start the application
Write-Host "`nStarting Font Image Maker..." -ForegroundColor Yellow
try {
    python font_image_maker.py
} catch {
    Write-Host "Error starting application: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "`nFont Image Maker has closed." -ForegroundColor Green
Read-Host "Press Enter to exit"
