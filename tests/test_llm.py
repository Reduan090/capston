# tests/test_llm.py
from utils.llm import ask_llm, get_embeddings
import pytest


def test_ask_llm():
    """Call the local Ollama-backed LLM if available; otherwise skip the test.

    This avoids failing the test suite on machines that don't have the Ollama
    server/binary installed (common for CI or fresh dev machines).
    """
    try:
        response = ask_llm("Test prompt", temperature=0.0)
    except ValueError as e:
        # ask_llm raises ValueError when it cannot contact Ollama.
        pytest.skip(f"Skipping LLM test: {e}")

    assert isinstance(response, str)
    assert len(response) > 0

def test_get_embeddings():
    emb = get_embeddings("Test text")
    assert isinstance(emb, list)
    assert len(emb) > 0