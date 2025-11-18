# modules/ai_writer.py
import streamlit as st
from utils.llm import ask_llm
from config import EXPORT_DIR, logger
import subprocess

def main():
    st.header("AI Writer & Outline Generator")
    title = st.text_input("Title")
    keywords = st.text_input("Keywords (comma-separated)")
    section = st.text_area("Co-write section (optional)")

    if st.button("Generate Outline"):
        prompt = f"Generate a detailed academic outline for '{title}' with keywords: {keywords}. Use formal tone."
        try:
            outline = ask_llm(prompt)
            st.markdown(outline)
        except ValueError as e:
            st.error(str(e))

    if st.button("Generate Article"):
        prompt = f"Write a full academic article for '{title}' with keywords {keywords}. Include {section} if provided. Academic tone."
        try:
            article = ask_llm(prompt)
            st.markdown(article)
        except ValueError as e:
            st.error(str(e))

    if st.button("Export to LaTeX"):
        if 'article' in locals():
            md_path = EXPORT_DIR / "article.md"
            with open(md_path, "w") as f:
                f.write(article)
            tex_path = EXPORT_DIR / "article.tex"
            try:
                subprocess.run(["pandoc", str(md_path), "-o", str(tex_path)], check=True)
                st.success(f"Exported to {tex_path}")
            except Exception as e:
                st.error("Pandoc export failed. Ensure pandoc is installed.")
                logger.error(f"Export error: {e}")
        else:
            st.warning("Generate article first.")