# Run the Streamlit app - Activate venv and start
# Usage: Open PowerShell and run: .\run_app.ps1

# Activate virtual environment
& "venv\Scripts\Activate.ps1"

# Run streamlit app
Write-Host "Starting Research Bot..." -ForegroundColor Green
Write-Host "App will open at http://localhost:8501" -ForegroundColor Cyan
Write-Host ""

streamlit run app.py
