# modules/topic_finder.py
import streamlit as st
from pathlib import Path
from utils.document_handler import load_document
from utils.nlp_helpers import extract_topics
from config import UPLOAD_DIR, logger

def main():
    st.header("Topic Finder")
    files = list(UPLOAD_DIR.iterdir())
    selected_file = st.selectbox("Select Document", [f.name for f in files])
    if selected_file:
        file_path = UPLOAD_DIR / selected_file
        try:
            text, _ = load_document(file_path)
            if st.button("Extract Topics"):
                topics = extract_topics(text[:50000])  # Limit for performance
                st.write(", ".join(topics))
        except ValueError as e:
            st.error(str(e))
            logger.error(str(e))