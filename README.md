# Research Bot - Capstone Project

An advanced AI-powered research assistant built with Streamlit, Ollama, LangChain, and FAISS. Supports PDF/DOCX/TXT/LaTeX handling, RAG chat, AI writing, literature reviews, citations, and more.

[![CI](https://github.com/Reduan090/capston/actions/workflows/ci.yml/badge.svg)](https://github.com/Reduan090/capston/actions/workflows/ci.yml)

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

## CI / Integration Tests

This repo uses GitHub Actions for CI. Unit tests run on GitHub-hosted runners and do not require Ollama (tests that need Ollama will be skipped or mocked). Full LLM integration tests that exercise a real Ollama server are run only on a self-hosted runner.

If you want to run integration tests with a real Ollama server, set up a self-hosted runner and label it `ollama`. The integration job is manual and will only run when triggered from the Actions UI.

Self-hosted runner setup (high level):

1. Provision a machine (Linux recommended) with enough RAM/disk for models.
2. Install GitHub Actions runner and register it with your repo; add the label `ollama` to the runner.
3. Install Ollama on that machine and pull the model(s):

```bash
# example (follow official Ollama instructions for your OS)
curl -sSL https://ollama.ai/install.sh | sh
ollama pull llama3
```

4. Ensure `ollama` is in PATH and that `ollama serve` can be started non-interactively.
5. Trigger the integration workflow from the Actions tab or via `workflow_dispatch`.

The CI workflow file is `.github/workflows/ci.yml` and includes both the hosted unit-test job and the manual self-hosted integration job.

## Installation
1. Clone repo: `git clone <url> && cd ResearchBot`

### Recommended (Windows, reproducible) — Conda environment
1. Install Miniconda/Anaconda if you don't have it.
2. Create the environment and install packages:

```powershell
conda env create -f environment.yml
conda activate capstone
```

3. Verify key imports:

```powershell
python -c "import streamlit, langchain, pymupdf; print('All packages ready!')"
```

4. In VS Code select the interpreter: `C:\Users\<you>\Miniconda3\envs\capstone\python.exe` to avoid linting warnings.

### Alternative (venv + pip — may fail for native packages on Windows)
1. Virtual env: `python -m venv venv && source venv/bin/activate` (Windows: `venv\Scripts\activate`)
2. Install deps: `pip install -r requirements.txt`

Note: On Windows, some native/binary packages (e.g., `faiss-cpu`, `pymupdf`) are easier to install via conda or require specific build tools.

## Configuration
- Edit `config.py` for Ollama model, embedding model, API keys (optional for Semantic Scholar).

## Running
1. Start Ollama: `ollama serve`
2. Run app: `streamlit run app.py`
3. Access: http://localhost:8501

## Testing
- Install pytest: Already in requirements.
- Run: `pytest tests/`

## Deployment
- For production, use Docker or deploy to Streamlit Cloud/Heroku.
- Add .env for secrets.

## License
MIT