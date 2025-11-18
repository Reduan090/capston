# modules/grammar_style.py
import streamlit as st
from utils.llm import ask_llm
from config import logger

def main():
    st.header("Grammar & Style Tools")
    text = st.text_area("Input Text")
    action = st.selectbox("Action", ["Grammar Check", "Paraphrase", "Translate to Academic English"])
    if st.button("Process"):
        try:
            if action == "Grammar Check":
                prompt = f"Correct grammar and enhance academic style: {text}"
            elif action == "Paraphrase":
                prompt = f"Paraphrase keeping technical meaning: {text}"
            else:
                prompt = f"Translate to English for Q1 journal publication: {text}"
            result = ask_llm(prompt)
            st.write(result)
        except ValueError as e:
            st.error(str(e))
            logger.error(str(e))