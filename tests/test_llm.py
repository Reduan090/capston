# tests/test_llm.py
from utils.llm import ask_llm, get_embeddings

def test_ask_llm():
    response = ask_llm("Test prompt", temperature=0.0)
    assert isinstance(response, str)
    assert len(response) > 0

def test_get_embeddings():
    emb = get_embeddings("Test text")
    assert isinstance(emb, list)
    assert len(emb) > 0