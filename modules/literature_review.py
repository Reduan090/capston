# modules/literature_review.py
import streamlit as st
from utils.api_helpers import fetch_papers
from utils.llm import ask_llm
from sklearn.cluster import KMeans
import numpy as np
from utils.llm import get_embeddings
from config import logger

def main():
    st.header("Literature Review Generator")
    query = st.text_input("Topic/Query")
    if st.button("Generate Review"):
        try:
            papers = fetch_papers(query)
            if not papers:
                st.warning("No papers found.")
                return

            summaries = []
            for paper in papers:
                abstract = paper.get('abstract', '')
                prompt = f"Summarize: Title: {paper['title']}. Abstract: {abstract}"
                summaries.append(ask_llm(prompt))

            # Cluster summaries
            embeds = np.array(get_embeddings(summaries))
            kmeans = KMeans(n_clusters=min(3, len(summaries)))
            clusters = kmeans.fit_predict(embeds)
            clustered = {}
            for i, cluster in enumerate(clusters):
                clustered.setdefault(cluster, []).append(summaries[i])

            cluster_prompt = f"Generate structured lit review from clustered summaries: {clustered}"
            review = ask_llm(cluster_prompt)
            st.markdown(review)
        except ValueError as e:
            st.error(str(e))