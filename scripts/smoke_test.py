"""Simple smoke test to validate document loading, chunking, embedding, and vector store creation.
Run this from the project root inside the `capstone` conda env:
    conda run -n capstone python scripts/smoke_test.py
"""
import sys
from pathlib import Path

# Add project root to path so imports like `config` and `utils` resolve when
# running the script from the project root or via `conda run`.
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from config import logger, UPLOAD_DIR
from utils.document_handler import load_document, chunk_text, create_vector_store, load_vector_store


def find_sample_file():
    up = Path(UPLOAD_DIR)
    if not up.exists():
        print(f"Upload dir {up} not found. Create uploads/ and place a small PDF or TXT to test.")
        return None
    # If a path is provided as a CLI arg, prefer that.
    import sys
    if len(sys.argv) > 1:
        candidate = Path(sys.argv[1])
        if candidate.exists():
            return candidate
        # allow relative to uploads dir
        candidate2 = up / sys.argv[1]
        if candidate2.exists():
            return candidate2

    files = sorted(up.glob('*'))
    if not files:
        print(f"No files in {up}. Add a small PDF or TXT to test the smoke flow.")
        return None
    # Prefer text-like files first to exercise chunking/embedding during smoke tests
    for ext in ('.txt', '.md', '.docx'):
        for f in files:
            if f.suffix.lower() == ext:
                return f
    return files[0]


def main():
    print("Starting smoke test...")
    f = find_sample_file()
    if not f:
        return
    print(f"Using sample file: {f}")
    try:
        text, meta = load_document(f)
        print("Loaded document; metadata:", meta)
        chunks = chunk_text(text)
        print(f"Split into {len(chunks)} chunks (first 2 shown):", chunks[:2])

        if not chunks:
            print("No text chunks were produced for this document (likely scanned PDF or empty). Skipping vector store creation.")
            return

        create_vector_store(chunks, f.name)
        print("Created vector store; now attempting to load it back")
        from config import VECTOR_DB_DIR
        index_path = Path(VECTOR_DB_DIR) / f"{f.name}.faiss"
        if not index_path.exists():
            print(f"Vector store not created at expected path: {index_path}")
            return
        idx, chunks2 = load_vector_store(f.name)
        print("Loaded vector store with", len(chunks2), "chunks")
        # Do a basic similarity search if FAISS loaded
        try:
            import numpy as np
            q = chunks2[0][:200]
            from utils.llm import get_embeddings
            emb = get_embeddings([q])
            if emb:
                emb = np.array(emb).astype('float32')
                D, I = idx.search(emb, k=3)
                print('Search distances:', D)
                print('Top indices:', I)
        except Exception as se:
            print('Search failed:', se)
    except Exception as e:
        print('Smoke test failed:', e)


if __name__ == '__main__':
    main()
