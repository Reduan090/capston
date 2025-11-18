# Implementation of document handling utilities (moved from utils/doc_handler.py)
import fitz  # PyMuPDF for metadata
import pdfplumber
from docx import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import faiss
import numpy as np
from typing import Dict, List, Tuple
from pathlib import Path
from config import VECTOR_DB_DIR, logger, UPLOAD_DIR
from langchain_community.document_loaders import TextLoader  # For .tex as text

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

def load_document(file_path: Path) -> Tuple[str, Dict]:
    """Load document and extract metadata.
    
    Args:
        file_path: Path to file.
    
    Returns:
        Tuple of text content and metadata dict.
    """
    ext = file_path.suffix.lower()
    text = ""
    metadata = {}
    try:
        if ext == ".pdf":
            with pdfplumber.open(file_path) as pdf:
                text = "\n".join(page.extract_text() or "" for page in pdf.pages)
            doc = fitz.open(file_path)
            metadata = doc.metadata  # Title, author, etc.
            doc.close()
        elif ext == ".docx":
            doc = Document(file_path)
            text = "\n".join(para.text for para in doc.paragraphs)
            metadata = {"title": file_path.stem, "authors": "Unknown"}  # No standard metadata
        elif ext in [".txt", ".tex"]:
            loader = TextLoader(str(file_path))
            docs = loader.load()
            text = docs[0].page_content
            metadata = {"title": file_path.stem, "authors": "Unknown"}
        logger.info(f"Loaded document: {file_path}")
        return text, metadata
    except Exception as e:
        logger.error(f"Document load error: {e}")
        raise ValueError("Unsupported or corrupted file.")

def chunk_text(text: str) -> List[str]:
    """Chunk text using LangChain splitter."""
    return text_splitter.split_text(text)

def create_vector_store(chunks: List[str], file_name: str) -> None:
    """Create and save FAISS index."""
    from utils.llm import get_embeddings
    embeddings = get_embeddings(chunks)
    d = len(embeddings[0])
    index = faiss.IndexFlatL2(d)
    index.add(np.array(embeddings).astype('float32'))
    index_path = VECTOR_DB_DIR / f"{file_name}.faiss"
    faiss.write_index(index, str(index_path))
    logger.info(f"Vector store created: {index_path}")

def load_vector_store(file_name: str) -> Tuple[faiss.Index, List[str]]:
    """Load FAISS index and chunks (chunks reloaded for simplicity)."""
    index_path = VECTOR_DB_DIR / f"{file_name}.faiss"
    if index_path.exists():
        index = faiss.read_index(str(index_path))
        # Reload chunks (in prod, serialize chunks with pickle)
        text, _ = load_document(UPLOAD_DIR / file_name)
        chunks = chunk_text(text)
        return index, chunks
    raise FileNotFoundError("Vector store not found.")
