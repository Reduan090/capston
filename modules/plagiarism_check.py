# modules/plagiarism_check.py
import streamlit as st
from utils.llm import get_embeddings
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
from config import logger, UPLOAD_DIR
from utils.document_handler import load_document
import numpy as np

def split_into_sentences(text: str) -> list:
    """Split text into sentences for granular plagiarism detection."""
    import re
    # Simple sentence splitter (handles . ! ?)
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s for s in sentences if s.strip()]

def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate overall similarity between two texts."""
    try:
        emb1 = get_embeddings([text1])
        emb2 = get_embeddings([text2])
        if not emb1 or not emb2:
            return 0.0
        sim = cosine_similarity([emb1[0]], [emb2[0]])[0][0]
        return float(sim)
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        return 0.0

def sentence_level_analysis(original: str, checked: str) -> tuple:
    """Analyze similarity at sentence level to detect paraphrasing."""
    orig_sentences = split_into_sentences(original)
    check_sentences = split_into_sentences(checked)
    
    if not orig_sentences or not check_sentences:
        return [], 0.0
    
    try:
        orig_embs = get_embeddings(orig_sentences)
        check_embs = get_embeddings(check_sentences)
        
        if not orig_embs or not check_embs:
            return [], 0.0
        
        # Compare each checked sentence against all original sentences
        results = []
        for i, check_emb in enumerate(check_embs):
            similarities = cosine_similarity([check_emb], orig_embs)[0]
            max_sim = float(np.max(similarities))
            max_idx = int(np.argmax(similarities))
            results.append({
                'checked_sent': check_sentences[i],
                'original_sent': orig_sentences[max_idx],
                'similarity': max_sim,
                'is_plagiarized': max_sim > 0.75
            })
        
        avg_sim = np.mean([r['similarity'] for r in results])
        return results, float(avg_sim)
    except Exception as e:
        logger.error(f"Sentence analysis error: {e}")
        return [], 0.0

def check_against_database(checked_text: str) -> dict:
    """Check text against uploaded documents in vector database."""
    try:
        from utils.database import get_all_files
        from utils.document_handler import load_vector_store, chunk_text, load_document
        
        uploaded_files = get_all_files() if hasattr(locals(), 'get_all_files') else []
        results = {}
        
        # Simple approach: check against available documents
        upload_dir = Path(UPLOAD_DIR)
        if upload_dir.exists():
            for file_path in upload_dir.glob('*'):
                if file_path.is_file() and file_path.suffix.lower() in ['.pdf', '.txt', '.docx']:
                    try:
                        text, _ = load_document(file_path)
                        sim = calculate_similarity(checked_text, text[:500])  # Check first 500 chars
                        if sim > 0.6:
                            results[file_path.name] = sim
                    except Exception:
                        pass
        
        return results
    except Exception as e:
        logger.error(f"Database check error: {e}")
        return {}

def main():
    st.header("🔍 Advanced Plagiarism & Consistency Checker")
    
    # Tabs for different check modes
    tab1, tab2, tab3 = st.tabs(["Direct Comparison", "Sentence-Level Analysis", "Database Check"])
    
    # Tab 1: Direct Comparison
    with tab1:
        st.subheader("Compare Two Texts")
        col1, col2 = st.columns(2)
        with col1:
            original = st.text_area("Original Text", height=200, key="original_direct")
        with col2:
            checked = st.text_area("Text to Check", height=200, key="checked_direct")
        
        if st.button("Check Similarity", key="btn_direct"):
            if original and checked:
                sim = calculate_similarity(original, checked)
                
                # Color-coded results
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Similarity Score", f"{sim:.2%}", delta=None)
                
                # Risk assessment
                if sim > 0.85:
                    st.error(f"⚠️ **HIGH PLAGIARISM RISK** ({sim:.2%})")
                    st.write("The texts are nearly identical or heavily paraphrased.")
                elif sim > 0.7:
                    st.warning(f"⚠️ **MODERATE PLAGIARISM RISK** ({sim:.2%})")
                    st.write("Significant similarity detected. Review for paraphrasing.")
                elif sim > 0.5:
                    st.info(f"ℹ️ **LOW-MODERATE SIMILARITY** ({sim:.2%})")
                    st.write("Some similarity detected. Check specific sections.")
                else:
                    st.success(f"✅ **ORIGINAL CONTENT** ({sim:.2%})")
                    st.write("Text appears to be original with minimal similarity.")
            else:
                st.error("❌ Please provide both texts.")
    
    # Tab 2: Sentence-Level Analysis
    with tab2:
        st.subheader("Detect Paraphrasing (Sentence-by-Sentence)")
        col1, col2 = st.columns(2)
        with col1:
            original_sent = st.text_area("Original Text", height=200, key="original_sent")
        with col2:
            checked_sent = st.text_area("Text to Check", height=200, key="checked_sent")
        
        if st.button("Analyze Sentences", key="btn_sent"):
            if original_sent and checked_sent:
                results, avg_sim = sentence_level_analysis(original_sent, checked_sent)
                
                st.metric("Average Similarity", f"{avg_sim:.2%}")
                
                if results:
                    st.write("### Sentence-by-Sentence Analysis")
                    for i, result in enumerate(results, 1):
                        with st.expander(f"Sentence {i} - {result['similarity']:.1%} match"):
                            st.write(f"**Checked:** {result['checked_sent']}")
                            st.write(f"**Best Match:** {result['original_sent']}")
                            st.write(f"**Similarity:** {result['similarity']:.2%}")
                            if result['is_plagiarized']:
                                st.error("⚠️ Potential plagiarism detected")
                            else:
                                st.success("✅ Original phrasing")
            else:
                st.error("❌ Please provide both texts.")
    
    # Tab 3: Check Against Database
    with tab3:
        st.subheader("Check Against Uploaded Documents")
        checked_text_db = st.text_area("Text to Check", height=200, key="checked_db")
        
        if st.button("Search Database", key="btn_db"):
            if checked_text_db:
                with st.spinner("Checking against uploaded documents..."):
                    matches = check_against_database(checked_text_db)
                
                if matches:
                    st.warning(f"⚠️ Found {len(matches)} matching documents:")
                    for filename, similarity in sorted(matches.items(), key=lambda x: x[1], reverse=True):
                        st.write(f"- **{filename}**: {similarity:.2%} similarity")
                else:
                    st.success("✅ No significant matches found in database.")
            else:
                st.error("❌ Please provide text to check.")