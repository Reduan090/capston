# Setup script - Install all dependencies in virtual environment
# Run this once after cloning the project

Write-Host "========================================" -ForegroundColor Green
Write-Host "Research Bot - Setup Script" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Check if venv exists
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate venv
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip setuptools wheel

# Install core auth requirements first
Write-Host "Installing auth dependencies (bcrypt, psycopg)..." -ForegroundColor Yellow
pip install bcrypt==4.1.2 "psycopg[binary]==3.2.12"

# Install all requirements
Write-Host "Installing all requirements from requirements.txt..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next: Run the app with:" -ForegroundColor Cyan
Write-Host "  .\run_app.ps1" -ForegroundColor Cyan
Write-Host ""
