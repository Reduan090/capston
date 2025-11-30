## CI / Integration Tests

The CI workflow file is `.github/workflows/ci.yml` and includes both the hosted unit-test job and the manual self-hosted integration job.

## Recommended model for local development

For development on a laptop with ~16GB RAM (CPU-only), we recommend using a small-to-medium model for good speed and low resource usage:

- **Recommended default:** `gemma3` (4B, ~3.3 GB) — good balance of quality and performance on CPU.
- **Smaller option:** `gemma3:1b` (1B, ~815 MB) — faster and uses less memory; useful if you see slow responses or memory issues.

To use the recommended model locally:

1. Install Ollama following its installer for Windows and open a new PowerShell.
2. Pull the model you want (examples):

```powershell
ollama pull gemma3
# or for the smaller model
ollama pull gemma3:1b
```

3. Start the Ollama server in a terminal:

```powershell
ollama serve
```

4. Ensure the project uses that model: `config.py` is set to `OLLAMA_MODEL = "gemma3"` by default.

5. Start the app (in the `capstone` conda env):

```powershell
conda activate capstone
streamlit run app.py
```

If you experience high latency or OOM errors, switch to `gemma3:1b`.
# Research Bot - Capstone Project

An advanced AI-powered research assistant built with Streamlit, Ollama, LangChain, and FAISS. Supports PDF/DOCX/TXT/LaTeX handling, RAG chat, AI writing, literature reviews, citations, and more.

## Features
- Modular Streamlit UI with tabs.
- Local LLM via Ollama (e.g., llama3).
- RAG for chatting with documents.
- AI writer with outline generation and LaTeX export.
- Literature review with API fetches and clustering.
- Citation management with SQLite storage.
- Plagiarism checker using embeddings.
- Topic finder with NLP.
- Grammar/style tools with paraphrasing/translation.
- Logging and error handling for robustness.

## Prerequisites
- Python 3.10+
- Ollama installed[](https://ollama.com) with model pulled: `ollama pull llama3`.
- FFmpeg for Whisper (optional speech-to-text): Install via OS package manager.
- Run `ollama serve` in a separate terminal.

## Installation (recommended: Conda on Windows)
1. Clone repo: `git clone <url> && cd ResearchBot`
2. Create the conda env (this project uses a conda environment for native packages):

```powershell
conda env create -f environment.yml
conda activate capstone
python -m pip install -r requirements-pip.txt
```

3. (Optional) For LaTeX export: Install `pandoc` (https://pandoc.org/installing.html)

## Configuration
- Edit `config.py` for Ollama model, embedding model, API keys (optional for Semantic Scholar).

## Running
1. Start Ollama (if you use local LLM): `ollama serve`
2. Start the app (recommended - PowerShell helper):

```powershell
.\run_app.ps1
# or for a local virtualenv: .\run_app_venv.ps1
```

3. Access: http://localhost:8501

Smoke test: to verify document ingestion and vector store creation without opening the UI run:

```powershell
conda run -n capstone python scripts/smoke_test.py
```

## Testing
- Install pytest: Already in requirements.
- Run: `pytest tests/`

## Deployment
- For production, use Docker or deploy to Streamlit Cloud/Heroku.
- Add .env for secrets.

## License
MIT