@echo off
REM Run Streamlit with conda environment 'capstone'
set ENV_NAME=capstone
echo Starting Streamlit in conda environment %ENV_NAME%...
conda run -n %ENV_NAME% python -m streamlit run app.py --server.port 8501
