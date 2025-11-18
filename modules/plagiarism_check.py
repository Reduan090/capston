# modules/plagiarism_check.py
import streamlit as st
from utils.llm import get_embeddings
from sklearn.metrics.pairwise import cosine_similarity
from config import logger

def main():
    st.header("Plagiarism & Consistency Checker")
    original = st.text_area("Original Text")
    checked = st.text_area("Checked/Paraphrased Text")
    if st.button("Check"):
        if original and checked:
            try:
                emb1 = get_embeddings(original)
                emb2 = get_embeddings(checked)
                sim = cosine_similarity([emb1], [emb2])[0][0]
                st.write(f"Similarity: {sim:.2f}")
                if sim > 0.9:
                    st.warning("High similarity - potential plagiarism.")
                elif sim > 0.7:
                    st.info("Moderate - check consistency.")
                else:
                    st.success("Low similarity - original.")
            except Exception as e:
                st.error(str(e))
                logger.error(str(e))
        else:
            st.error("Provide both texts.")