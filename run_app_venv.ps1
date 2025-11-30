# Run the Streamlit app using the local .venv virtual environment
# Usage: Open PowerShell and run: .\run_app_venv.ps1

$venvPath = ".\.venv\Scripts\python.exe"
if (-Not (Test-Path $venvPath)) {
    Write-Host "No .venv found at $venvPath. Create a virtualenv first or use run_app.ps1 for conda." ; exit 1
}
& $venvPath -m streamlit run app.py --server.port 8501
