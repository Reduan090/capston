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

## Installation
1. Clone repo: `git clone <url> && cd ResearchBot`
2. Virtual env: `python -m venv venv && source venv/bin/activate` (Windows: `venv\Scripts\activate`)
3. Install deps: `pip install -r requirements.txt`
4. (Optional) For LaTeX export: Install pandoc[](https://pandoc.org/installing.html)

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