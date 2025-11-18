# modules/ask_paper.py
import streamlit as st
from pathlib import Path
import numpy as np
from utils.document_handler import load_vector_store
from utils.llm import ask_llm, get_embeddings
from config import UPLOAD_DIR, logger

def main():
    st.header("Ask a Paper (RAG Chat)")
    files = [f.name for f in UPLOAD_DIR.iterdir() if f.suffix in [".pdf", ".docx", ".txt", ".tex"]]
    selected_file = st.selectbox("Select Document", files)
    if selected_file:
        try:
            index, chunks = load_vector_store(selected_file)
            question = st.text_input("Question")
            if st.button("Ask"):
                query_emb = np.array(get_embeddings(question)).astype('float32')
                D, I = index.search(query_emb, k=5)
                relevant = [chunks[i] for i in I[0] if i < len(chunks)]
                prompt = f"Answer '{question}' using context: {' '.join(relevant)}"
                answer = ask_llm(prompt)
                st.write(answer)
        except FileNotFoundError as e:
            st.error("Process document first.")
            logger.error(str(e))