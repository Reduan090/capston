# tests/test_document_handler.py
from utils.document_handler import load_document
from pathlib import Path

def test_load_document():
    # Create a test file
    test_path = Path("test.txt")
    with open(test_path, "w") as f:
        f.write("Test content")
    text, meta = load_document(test_path)
    assert text == "Test content"
    assert meta["title"] == "test"
    test_path.unlink()