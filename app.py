# app.py
import streamlit as st
from utils.database import init_db
from modules import (upload_pdf, ai_writer, literature_review, ask_paper,
                     topic_finder, grammar_style, citation_tool, plagiarism_check)
from config import logger
from setup_logging import setup_logging
from utils.cache_cleaner import clean_all_caches

init_db()
logger = setup_logging() if 'setup_logging' in globals() else logger  # Optional

# Sidebar for cache management
with st.sidebar:
    st.header("⚙️ System Management")
    if st.button("🧹 Clean Cache", help="Remove Python cache and old vector databases"):
        with st.spinner("Cleaning cache..."):
            results = clean_all_caches()
            st.success(f"✅ Cache cleaned! Freed {results['total_space_freed_mb']:.2f} MB")
            if results['pycache']['pycache_dirs_removed'] > 0:
                st.info(f"Removed {results['pycache']['pycache_dirs_removed']} __pycache__ directories")
            if results['vector_db']['vector_dbs_removed'] > 0:
                st.info(f"Removed {results['vector_db']['vector_dbs_removed']} old vector databases")

st.title("Research Bot - Advanced AI Research Assistant")

tab_names = [
    "Upload Document", "AI Writer", "Literature Review", "Ask a Paper",
    "Topic Finder", "Grammar & Style", "Citation/Reference Tool", "Plagiarism & Consistency Check"
]

tabs = st.tabs(tab_names)

with tabs[0]:
    upload_pdf.main()

with tabs[1]:
    ai_writer.main()

with tabs[2]:
    literature_review.main()

with tabs[3]:
    ask_paper.main()

with tabs[4]:
    topic_finder.main()

with tabs[5]:
    grammar_style.main()

with tabs[6]:
    citation_tool.main()

with tabs[7]:
    plagiarism_check.main()