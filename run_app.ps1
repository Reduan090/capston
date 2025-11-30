# Run the Streamlit app using the conda 'capstone' environment
# Usage: Open PowerShell and run: .\run_app.ps1

$envName = "capstone"
$script = "python -m streamlit run app.py --server.port 8501"
Write-Host "Starting Streamlit in conda environment '$envName'..."
conda run -n $envName $script
