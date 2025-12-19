# modules/literature_review.py
import streamlit as st
from utils.api_helpers import fetch_papers
from utils.llm import ask_llm, get_embeddings
from sklearn.cluster import KMeans
import numpy as np
from pathlib import Path
from config import logger, UPLOAD_DIR
from utils.document_handler import load_document

def generate_review_from_uploaded_docs():
    """Generate literature review from uploaded documents"""
    files = [f for f in UPLOAD_DIR.iterdir() if f.suffix.lower() in ['.pdf', '.docx', '.txt', '.tex']]
    
    if not files:
        st.warning("No uploaded documents found. Please upload documents first.")
        return
    
    selected_files = st.multiselect(
        "Select documents to include in review",
        [f.name for f in files],
        default=[f.name for f in files[:min(5, len(files))]]
    )
    
    review_depth = st.select_slider(
        "Review Depth",
        options=["Quick Summary", "Standard", "Comprehensive"],
        value="Standard"
    )
    
    if st.button("Generate Review from Uploaded Documents", key="gen_review_docs"):
        if not selected_files:
            st.warning("Please select at least one document.")
            return
            
        with st.spinner(f"Analyzing {len(selected_files)} documents..."):
            try:
                # Extract content from selected documents
                doc_summaries = []
                doc_info = []
                
                for filename in selected_files:
                    file_path = UPLOAD_DIR / filename
                    text, metadata = load_document(file_path)
                    
                    # Extract key information
                    chunk_size = 2000 if review_depth == "Quick Summary" else 5000 if review_depth == "Standard" else 10000
                    excerpt = text[:chunk_size]
                    
                    summary_prompt = f"""Analyze this research document and provide:
1. Main research question/objective
2. Key methodology
3. Major findings
4. Conclusions

Document: {filename}
Content: {excerpt}"""
                    
                    summary = ask_llm(summary_prompt, temperature=0.3)
                    doc_summaries.append(summary)
                    doc_info.append({'filename': filename, 'summary': summary})
                
                # Generate thematic clusters
                st.write("### 📊 Thematic Analysis")
                if len(doc_summaries) >= 2:
                    embeds = get_embeddings(doc_summaries)
                    if embeds:
                        embeds_array = np.array(embeds)
                        n_clusters = min(3, len(doc_summaries))
                        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                        clusters = kmeans.fit_predict(embeds_array)
                        
                        # Group by clusters
                        clustered = {}
                        for i, cluster in enumerate(clusters):
                            if cluster not in clustered:
                                clustered[cluster] = []
                            clustered[cluster].append(doc_info[i])
                        
                        # Display clusters
                        for cluster_id, docs in clustered.items():
                            with st.expander(f"📚 Theme {cluster_id + 1} ({len(docs)} documents)"):
                                for doc in docs:
                                    st.write(f"**{doc['filename']}**")
                                    st.write(doc['summary'][:300] + "...")
                
                # Generate comprehensive literature review
                st.write("### 📝 Literature Review")
                
                review_prompt = f"""Generate a comprehensive literature review based on these {len(doc_summaries)} research documents.

Structure the review with:
1. **Introduction**: Overview of the research area
2. **Thematic Analysis**: Identify and discuss major themes
3. **Methodological Approaches**: Compare methodologies used
4. **Key Findings**: Synthesize major findings across studies
5. **Research Gaps**: Identify areas needing further research
6. **Conclusion**: Summary and future directions

Document Summaries:
{chr(10).join([f"Document {i+1} ({doc_info[i]['filename']}): {summary}" for i, summary in enumerate(doc_summaries)])}

Generate a well-structured, academic literature review."""
                
                review = ask_llm(review_prompt, temperature=0.5)
                st.markdown(review)
                
                # Export option
                if st.button("📥 Export Review"):
                    from config import EXPORT_DIR
                    export_path = EXPORT_DIR / f"literature_review_{len(selected_files)}_docs.md"
                    with open(export_path, 'w', encoding='utf-8') as f:
                        f.write(f"# Literature Review\n\n")
                        f.write(f"Based on {len(selected_files)} documents\n\n")
                        f.write(review)
                    st.success(f"Exported to {export_path.name}")
                    
            except Exception as e:
                st.error(f"Error generating review: {str(e)}")
                logger.error(f"Literature review error: {e}")

def generate_review_from_external_sources():
    """Generate literature review from external sources (Semantic Scholar, arXiv)"""
    query = st.text_input("Research Topic/Query", placeholder="e.g., machine learning in healthcare")
    max_papers = st.slider("Number of papers", 5, 20, 10)
    
    if st.button("Search External Sources", key="gen_review_external"):
        with st.spinner(f"Searching for papers on '{query}'..."):
            try:
                papers = fetch_papers(query, limit=max_papers)
                if not papers:
                    st.warning("No papers found. Try a different query.")
                    return

                # Show found papers
                st.write(f"### Found {len(papers)} papers")
                
                summaries = []
                for i, paper in enumerate(papers):
                    with st.expander(f"📄 {paper.get('title', 'Untitled')[:100]}..."):
                        st.write(f"**Year:** {paper.get('year', 'N/A')}")
                        st.write(f"**Authors:** {', '.join([a.get('name', '') for a in paper.get('authors', [])])[:200]}")
                        abstract = paper.get('abstract', 'No abstract available')
                        st.write(f"**Abstract:** {abstract[:500]}...")
                        
                    # Summarize each paper
                    abstract = paper.get('abstract', '')
                    if abstract:
                        prompt = f"Summarize this research paper in 3-4 sentences:\nTitle: {paper.get('title', '')}\nAbstract: {abstract}"
                        summaries.append(ask_llm(prompt, temperature=0.3))

                if not summaries:
                    st.warning("No abstracts available to generate review.")
                    return

                # Cluster and generate review
                st.write("### 📝 Synthesized Literature Review")
                embeds = get_embeddings(summaries)
                if embeds:
                    embeds_array = np.array(embeds)
                    kmeans = KMeans(n_clusters=min(3, len(summaries)), random_state=42)
                    clusters = kmeans.fit_predict(embeds_array)
                    clustered = {}
                    for i, cluster in enumerate(clusters):
                        clustered.setdefault(cluster, []).append(summaries[i])

                    review_prompt = f"""Generate a structured literature review on "{query}" based on these clustered summaries:

{chr(10).join([f"Theme {k+1}: {', '.join(v[:2])}" for k, v in clustered.items()])}

Provide:
1. Overview of the research landscape
2. Major themes and approaches
3. Key findings and consensus
4. Emerging trends
5. Research gaps"""

                    review = ask_llm(review_prompt, temperature=0.5)
                    st.markdown(review)
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
                logger.error(f"External review error: {e}")

def main():
    st.header("📚 Literature Review Generator")
    
    tab1, tab2 = st.tabs(["📁 From Uploaded Documents", "🌐 From External Sources"])
    
    with tab1:
        st.write("Generate a comprehensive literature review from your uploaded documents.")
        generate_review_from_uploaded_docs()
    
    with tab2:
        st.write("Search and synthesize literature from Semantic Scholar and arXiv.")
        generate_review_from_external_sources()