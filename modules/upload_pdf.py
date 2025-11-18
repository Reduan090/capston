# modules/upload_pdf.py
import streamlit as st
from pathlib import Path
from utils.document_handler import load_document, chunk_text, create_vector_store
from utils.database import add_reference  # For metadata
from config import UPLOAD_DIR, logger

def main():
    st.header("Upload Document")
    uploaded_file = st.file_uploader("Upload PDF/DOCX/TXT/LaTeX", type=["pdf", "docx", "txt", "tex"])
    if uploaded_file:
        file_path = UPLOAD_DIR / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        try:
            text, metadata = load_document(file_path)
            chunks = chunk_text(text)
            create_vector_store(chunks, uploaded_file.name)
            # Add to DB if metadata available
            if metadata.get("title"):
                add_reference(
                    metadata.get("title", uploaded_file.name),
                    metadata.get("author", "Unknown"),
                    metadata.get("creationDate", "Unknown")[:4],  # Year approx
                    metadata.get("doi", ""),
                    ""  # BibTeX placeholder
                )
            st.success("Document processed, vectorized, and metadata stored!")
        except ValueError as e:
            st.error(str(e))
            logger.error(str(e))